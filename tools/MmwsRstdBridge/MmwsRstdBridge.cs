/*
 * MmwsRstdBridge — Native .NET Framework console app for RSTD communication.
 *
 * Replaces Pythonnet-based RSTD transport. Directly references RtttNetClientAPI.dll
 * from the TI mmWave Studio installation.
 *
 * API Signatures (from DLL introspection):
 *   int Init()
 *   int Init(string log_file)
 *   int Connect(string ip_addr)
 *   int Connect(string ip_addr, int port)
 *   bool IsConnected()
 *   int SendCommand(string lua_str, ref Object[] res_arr)
 *   int SendCommand(string lua_str, ref Object[] res_arr, int send_timeout, int recv_timeout, RstdNetCmdID id)
 *   int RunScript(string lua_str, ref Object[] res_arr)
 *   string GetLastError()
 *   string GetErrMsg(int err_code)
 *   void SendStopCommand()
 *   int Disconnect()
 *   int Close()
 *
 * Modes:
 *   ping           Init + Connect + IsConnected + GetLastError
 *   send-command   Above + SendCommand('dofile([[script_path]])', ref res)
 *   run-script     Above + RunScript(script_path, ref res)
 *   introspect     List public methods on RtttNetClient
 *
 * Usage:
 *   MmwsRstdBridge.exe --mode ping --result result.json [--host 127.0.0.1] [--port 2777] [--verbose]
 *   MmwsRstdBridge.exe --mode send-command --script smoke.lua --result result.json
 *   MmwsRstdBridge.exe --mode run-script --script smoke.lua --result result.json
 *   MmwsRstdBridge.exe --mode introspect --result result.json
 *
 * Build:
 *   C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe /target:exe /platform:x86 ^
 *     /reference:"<path_to_RtttNetClientAPI.dll>" /out:MmwsRstdBridge.exe MmwsRstdBridge.cs
 */

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;

namespace MmwsRstdBridge
{
    class Program
    {
        // --- Assembly Resolve ---
        // RtttNetClientAPI.dll may not be beside our .exe.
        // Register an AssemblyResolve handler to load it from the mmWave Studio path.
        private static string _dllSearchDir = null;

        static Assembly ResolveAssembly(object sender, ResolveEventArgs args)
        {
            if (_dllSearchDir == null) return null;

            string simpleName = new AssemblyName(args.Name).Name;
            string candidate = Path.Combine(_dllSearchDir, simpleName + ".dll");
            if (File.Exists(candidate))
            {
                return Assembly.LoadFrom(candidate);
            }
            return null;
        }

        // --- Simple JSON builder (no external deps, C# 5 compatible) ---
        public class JsonBuilder
        {
            private List<string> _entries = new List<string>();
            private List<string> _steps = new List<string>();
            private Stopwatch _totalTimer = new Stopwatch();

            public JsonBuilder()
            {
                _totalTimer.Start();
            }

            public void AddString(string key, string value)
            {
                if (value == null)
                    _entries.Add("\"" + Esc(key) + "\":null");
                else
                    _entries.Add("\"" + Esc(key) + "\":\"" + Esc(value) + "\"");
            }

            public void AddInt(string key, int value)
            {
                _entries.Add("\"" + Esc(key) + "\":" + value);
            }

            public void AddLong(string key, long value)
            {
                _entries.Add("\"" + Esc(key) + "\":" + value);
            }

            public void AddBool(string key, bool value)
            {
                _entries.Add("\"" + Esc(key) + "\":" + (value ? "true" : "false"));
            }

            public void AddNull(string key)
            {
                _entries.Add("\"" + Esc(key) + "\":null");
            }

            public void AddRaw(string key, string rawJson)
            {
                _entries.Add("\"" + Esc(key) + "\":" + rawJson);
            }

            public void AddStep(string name, long timeMs, string result)
            {
                _steps.Add("{\"step\":\"" + Esc(name) + "\",\"time_ms\":" + timeMs
                    + ",\"result\":\"" + Esc(result ?? "null") + "\"}");
            }

            public void AddStep(string name, long timeMs, int result)
            {
                _steps.Add("{\"step\":\"" + Esc(name) + "\",\"time_ms\":" + timeMs
                    + ",\"result\":" + result + "}");
            }

            public string Build()
            {
                _totalTimer.Stop();
                var sb = new StringBuilder();
                sb.Append("{");

                for (int i = 0; i < _entries.Count; i++)
                {
                    if (i > 0) sb.Append(",");
                    sb.Append(_entries[i]);
                }

                if (_entries.Count > 0) sb.Append(",");
                sb.Append("\"elapsed_ms\":" + _totalTimer.ElapsedMilliseconds);

                sb.Append(",\"steps\":[");
                for (int i = 0; i < _steps.Count; i++)
                {
                    if (i > 0) sb.Append(",");
                    sb.Append(_steps[i]);
                }
                sb.Append("]");

                sb.Append("}");
                return sb.ToString();
            }

            private static string Esc(string s)
            {
                if (s == null) return "";
                return s.Replace("\\", "\\\\").Replace("\"", "\\\"")
                        .Replace("\n", "\\n").Replace("\r", "\\r")
                        .Replace("\t", "\\t");
            }
        }

        // --- Argument parsing ---
        static string GetArg(string[] args, string name, string defaultValue = null)
        {
            for (int i = 0; i < args.Length - 1; i++)
            {
                if (args[i].Equals(name, StringComparison.OrdinalIgnoreCase))
                    return args[i + 1];
            }
            return defaultValue;
        }

        static bool HasFlag(string[] args, string name)
        {
            for (int i = 0; i < args.Length; i++)
            {
                if (args[i].Equals(name, StringComparison.OrdinalIgnoreCase))
                    return true;
            }
            return false;
        }

        static void Log(bool verbose, string msg)
        {
            if (verbose) Console.Error.WriteLine("[bridge] " + msg);
        }

        // --- Main ---
        static int Main(string[] args)
        {
            string mode = GetArg(args, "--mode", "ping");
            string host = GetArg(args, "--host", "127.0.0.1");
            string portStr = GetArg(args, "--port", "2777");
            string scriptPath = GetArg(args, "--script");
            string resultPath = GetArg(args, "--result", "worker_result.json");
            string dllDir = GetArg(args, "--dll-dir");
            bool verbose = HasFlag(args, "--verbose");
            string apartmentStr = GetArg(args, "--apartment", "mta").ToLowerInvariant();
            ApartmentState apartment = apartmentStr == "sta" ? ApartmentState.STA : ApartmentState.MTA;

            int port;
            if (!int.TryParse(portStr, out port))
            {
                Console.Error.WriteLine("Invalid port: " + portStr);
                return 1;
            }

            // Set up AssemblyResolve for RtttNetClientAPI.dll
            if (dllDir != null)
            {
                _dllSearchDir = dllDir;
            }
            else
            {
                // Check known TI installation paths
                string[] tiPaths = new string[]
                {
                    @"C:\ti\mmwave_studio_03_01_04_04\mmWaveStudio\Clients\RtttNetClientController",
                    @"C:\ti\mmwave_studio_03_00_00_14\mmWaveStudio\Clients\RtttNetClientController",
                };
                foreach (string p in tiPaths)
                {
                    if (Directory.Exists(p))
                    {
                        _dllSearchDir = p;
                        break;
                    }
                }
                // Fallback: beside our exe
                if (_dllSearchDir == null)
                {
                    _dllSearchDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                }
            }

            AppDomain.CurrentDomain.AssemblyResolve += ResolveAssembly;

            Log(verbose, "mode=" + mode);
            Log(verbose, "host=" + host + " port=" + port);
            Log(verbose, "script=" + (scriptPath ?? "(none)"));
            Log(verbose, "result=" + resultPath);
            Log(verbose, "dll-dir=" + _dllSearchDir);

            var json = new JsonBuilder();
            json.AddString("mode", mode);

            try
            {
                // Dispatch via a separate class so RtttNetClientAPI
                // is only JIT-loaded after AssemblyResolve is registered.
                Thread t = new Thread(() => {
                    try {
                        RstdBridge.Dispatch(json, mode, host, port, scriptPath, verbose);
                    } catch (Exception innerEx) {
                        json.AddString("exception", innerEx.GetType().Name + ": " + innerEx.Message);
                        Log(verbose, "THREAD EXCEPTION: " + innerEx);
                    }
                });
                t.SetApartmentState(apartment);
                t.Start();
                t.Join();
            }
            catch (Exception ex)
            {
                json.AddString("exception", ex.GetType().Name + ": " + ex.Message);
                Log(verbose, "EXCEPTION: " + ex);
            }

            // Write result JSON
            string output = json.Build();
            try
            {
                File.WriteAllText(resultPath, output, new UTF8Encoding(false));
                Log(verbose, "Result written to: " + resultPath);
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("Failed to write result: " + ex.Message);
                // Fallback: print to stdout
                Console.Out.WriteLine(output);
                return 2;
            }

            return 0;
        }
    }

    // ==================================================================
    // RstdBridge — separate class to isolate RtttNetClientAPI references.
    // This class is only JIT-loaded when Dispatch() is first called,
    // which is after AssemblyResolve has been registered.
    // ==================================================================
    class RstdBridge
    {
        static void Log(bool verbose, string msg)
        {
            if (verbose) Console.Error.WriteLine("[bridge] " + msg);
        }
        
        static void StepStart(string stepName)
        {
            Console.WriteLine("STEP_START:" + stepName);
            Console.Out.Flush();
        }
        
        static void StepDone(string stepName)
        {
            Console.WriteLine("STEP_DONE:" + stepName);
            Console.Out.Flush();
        }

        public static void Dispatch(Program.JsonBuilder json, string mode, string host, int port, string scriptPath, bool verbose)
        {
            try
            {
                switch (mode.ToLowerInvariant())
                {
                    case "ping":
                        DoPing(json, host, port, verbose);
                        break;
                    case "send-command":
                        if (string.IsNullOrEmpty(scriptPath))
                        {
                            json.AddString("exception", "send-command requires --script");
                            break;
                        }
                        DoSendCommand(json, host, port, scriptPath, verbose);
                        break;
                    case "send-inline":
                        DoSendInline(json, host, port, verbose);
                        break;
                    case "run-script":
                        if (string.IsNullOrEmpty(scriptPath))
                        {
                            json.AddString("exception", "run-script requires --script");
                            break;
                        }
                        DoRunScript(json, host, port, scriptPath, verbose);
                        break;
                    case "introspect":
                        DoIntrospect(json, verbose);
                        break;
                    default:
                        json.AddString("exception", "Unknown mode: " + mode);
                        break;
                }
            }
            finally
            {
                // Always disconnect/close to prevent the process from hanging
                try
                {
                    if (mode.ToLowerInvariant() != "introspect")
                    {
                        StepStart("Disconnect");
                        RtttNetClientAPI.RtttNetClient.Disconnect();
                        StepDone("Disconnect");
                        StepStart("Close");
                        RtttNetClientAPI.RtttNetClient.Close();
                        StepDone("Close");
                        Log(verbose, "Disconnect/Close done");
                    }
                }
                catch (Exception) { /* ignore cleanup errors */ }
            }
        }

        // ------------------------------------------------------------------
        // Init + Connect helper
        // ------------------------------------------------------------------
        static bool DoInitAndConnect(Program.JsonBuilder json, string host, int port, bool verbose)
        {
            var sw = new Stopwatch();

            // Init
            Log(verbose, "Init()...");
            StepStart("Init");
            sw.Restart();
            int initRet = RtttNetClientAPI.RtttNetClient.Init();
            StepDone("Init");
            sw.Stop();
            json.AddInt("init_return", initRet);
            json.AddStep("init", sw.ElapsedMilliseconds, initRet);
            Log(verbose, "Init() = " + initRet + " (" + sw.ElapsedMilliseconds + "ms)");

            if (initRet != 0)
            {
                json.AddString("exception", "Init() returned " + initRet);
                return false;
            }

            // Connect
            Log(verbose, "Connect(" + host + ", " + port + ")...");
            StepStart("Connect");
            sw.Restart();
            int connectRet = RtttNetClientAPI.RtttNetClient.Connect(host, port);
            StepDone("Connect");
            sw.Stop();
            json.AddInt("connect_return", connectRet);
            json.AddStep("connect", sw.ElapsedMilliseconds, connectRet);
            Log(verbose, "Connect() = " + connectRet + " (" + sw.ElapsedMilliseconds + "ms)");

            // IsConnected
            StepStart("IsConnected");
            sw.Restart();
            bool isConn = RtttNetClientAPI.RtttNetClient.IsConnected();
            StepDone("IsConnected");
            sw.Stop();
            json.AddBool("is_connected", isConn);
            json.AddStep("is_connected", sw.ElapsedMilliseconds, isConn ? "true" : "false");
            Log(verbose, "IsConnected() = " + isConn + " (" + sw.ElapsedMilliseconds + "ms)");

            return true;
        }

        // ------------------------------------------------------------------
        // Error state
        // ------------------------------------------------------------------
        static void DoGetErrorState(Program.JsonBuilder json, int lastReturnCode, bool verbose)
        {
            var sw = new Stopwatch();

            // GetLastError() -> string
            sw.Restart();
            try
            {
                string lastErr = RtttNetClientAPI.RtttNetClient.GetLastError();
                sw.Stop();
                json.AddString("last_error", lastErr);
                json.AddStep("get_last_error", sw.ElapsedMilliseconds, lastErr ?? "null");
                Log(verbose, "GetLastError() = " + (lastErr ?? "null"));
            }
            catch (Exception ex)
            {
                sw.Stop();
                json.AddString("last_error", "error: " + ex.Message);
                Log(verbose, "GetLastError() threw: " + ex.Message);
            }

            // GetErrMsg(int err_code) -> string
            sw.Restart();
            try
            {
                string errMsg = RtttNetClientAPI.RtttNetClient.GetErrMsg(lastReturnCode);
                sw.Stop();
                if (string.IsNullOrEmpty(errMsg))
                    json.AddNull("err_msg");
                else
                    json.AddString("err_msg", errMsg);
                json.AddStep("get_err_msg", sw.ElapsedMilliseconds, errMsg ?? "null");
                Log(verbose, "GetErrMsg(" + lastReturnCode + ") = " + (errMsg ?? "null"));
            }
            catch (Exception ex)
            {
                sw.Stop();
                json.AddNull("err_msg");
                Log(verbose, "GetErrMsg() threw: " + ex.Message);
            }
        }

        // ------------------------------------------------------------------
        // Mode: ping
        // ------------------------------------------------------------------
        static void DoPing(Program.JsonBuilder json, string host, int port, bool verbose)
        {
            if (!DoInitAndConnect(json, host, port, verbose))
                return;

            DoGetErrorState(json, 0, verbose);
            json.AddNull("exception");
        }

        // ------------------------------------------------------------------
        // Mode: send-command
        // ------------------------------------------------------------------
        static void DoSendCommand(Program.JsonBuilder json, string host, int port, string scriptPath, bool verbose)
        {
            if (!DoInitAndConnect(json, host, port, verbose))
                return;

            // Build dofile command with safe Lua [[ ]] quoting and forward slashes
            string absPath = Path.GetFullPath(scriptPath).Replace("\\", "/");
            string luaCmd = "dofile([[" + absPath + "]])";
            json.AddString("lua_command", luaCmd);

            Log(verbose, "SendCommand: " + luaCmd);

            // SendCommand(string lua_str, out Object[] res_arr)
            object[] resArr;
            var sw = new Stopwatch();
            StepStart("SendCommand");
            sw.Restart();
            int sendRet = RtttNetClientAPI.RtttNetClient.SendCommand(luaCmd, out resArr);
            StepDone("SendCommand");
            sw.Stop();
            json.AddInt("send_return", sendRet);
            json.AddStep("send_command", sw.ElapsedMilliseconds, sendRet);
            Log(verbose, "SendCommand() = " + sendRet + " (" + sw.ElapsedMilliseconds + "ms)");

            // Log response array if any
            if (resArr != null && resArr.Length > 0)
            {
                var resSb = new StringBuilder("[");
                for (int i = 0; i < resArr.Length; i++)
                {
                    if (i > 0) resSb.Append(",");
                    if (resArr[i] == null)
                        resSb.Append("null");
                    else
                        resSb.Append("\"" + resArr[i].ToString().Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"");
                }
                resSb.Append("]");
                json.AddRaw("send_response", resSb.ToString());
                Log(verbose, "Response array: " + resSb);
            }
            else
            {
                json.AddNull("send_response");
            }

            DoGetErrorState(json, sendRet, verbose);
            json.AddNull("exception");
        }

        // ------------------------------------------------------------------
        // Mode: run-script
        // ------------------------------------------------------------------
        
        static void DoSendInline(Program.JsonBuilder json, string host, int port, bool verbose)
        {
            if (!DoInitAndConnect(json, host, port, verbose))
                return;

            string luaCmd = "WriteToLog(\"INLINE_SEND_TEST\\n\")";
            json.AddString("lua_command", luaCmd);

            Log(verbose, "SendInline: " + luaCmd);
            
            StepStart("send_inline");
            object[] resArr;
            var sw = new Stopwatch();
            StepStart("SendCommand");
            sw.Restart();
            int sendRet = RtttNetClientAPI.RtttNetClient.SendCommand(luaCmd, out resArr);
            StepDone("SendCommand");
            sw.Stop();
            StepDone("send_inline");
            
            json.AddInt("send_return", sendRet);
            json.AddStep("send_inline", sw.ElapsedMilliseconds, sendRet);
            Log(verbose, "SendInline() = " + sendRet + " (" + sw.ElapsedMilliseconds + "ms)");

            DoGetErrorState(json, sendRet, verbose);
            json.AddNull("exception");
        }

        static void DoRunScript(Program.JsonBuilder json, string host, int port, string scriptPath, bool verbose)
        {
            if (!DoInitAndConnect(json, host, port, verbose))
                return;

            string absPath = Path.GetFullPath(scriptPath);
            if (!File.Exists(absPath))
            {
                json.AddString("exception", "Script file not found: " + absPath);
                return;
            }

            json.AddString("script_path", absPath);
            Log(verbose, "RunScript: " + absPath);

            // RunScript(string lua_str, out Object[] res_arr)
            object[] resArr;
            var sw = new Stopwatch();
            StepStart("RunScript");
            sw.Restart();
            int runRet = RtttNetClientAPI.RtttNetClient.RunScript(absPath, out resArr);
            StepDone("RunScript");
            sw.Stop();
            json.AddInt("runscript_return", runRet);
            json.AddStep("run_script", sw.ElapsedMilliseconds, runRet);
            Log(verbose, "RunScript() = " + runRet + " (" + sw.ElapsedMilliseconds + "ms)");

            // Log response array if any
            if (resArr != null && resArr.Length > 0)
            {
                var resSb = new StringBuilder("[");
                for (int i = 0; i < resArr.Length; i++)
                {
                    if (i > 0) resSb.Append(",");
                    if (resArr[i] == null)
                        resSb.Append("null");
                    else
                        resSb.Append("\"" + resArr[i].ToString().Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"");
                }
                resSb.Append("]");
                json.AddRaw("run_response", resSb.ToString());
                Log(verbose, "Response array: " + resSb);
            }
            else
            {
                json.AddNull("run_response");
            }

            DoGetErrorState(json, runRet, verbose);
            json.AddNull("exception");
        }

        // ------------------------------------------------------------------
        // Mode: introspect
        // ------------------------------------------------------------------
        static void DoIntrospect(Program.JsonBuilder json, bool verbose)
        {
            var t = typeof(RtttNetClientAPI.RtttNetClient);
            var methods = t.GetMethods(BindingFlags.Public | BindingFlags.Static | BindingFlags.DeclaredOnly);

            var sb = new StringBuilder("[");
            for (int i = 0; i < methods.Length; i++)
            {
                if (i > 0) sb.Append(",");
                var m = methods[i];
                var parms = m.GetParameters();
                var parmStr = new StringBuilder();
                for (int j = 0; j < parms.Length; j++)
                {
                    if (j > 0) parmStr.Append(", ");
                    string byRef = parms[j].ParameterType.IsByRef ? "ref " : "";
                    string typeName = parms[j].ParameterType.IsByRef
                        ? parms[j].ParameterType.GetElementType().Name
                        : parms[j].ParameterType.Name;
                    parmStr.Append(byRef + typeName + " " + parms[j].Name);
                }

                string sigStr = m.ReturnType.Name + " " + m.Name + "(" + parmStr + ")";
                sb.Append("{\"signature\":\"" + sigStr.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"}");

                Log(verbose, "  " + sigStr);
            }
            sb.Append("]");

            json.AddRaw("methods", sb.ToString());
            json.AddNull("exception");
        }
    }
}

