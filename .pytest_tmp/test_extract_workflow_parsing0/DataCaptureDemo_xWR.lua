
-- Some comment
ar1.SOPControl(2)
if (ar1.Connect(4, 921600, 1000) == 0) then
if (ar1.DownloadBSSFw("fw.bin") == 0) then
-- ignore me ar1.RfInit()
if (ar1.AdvanceFrameConfig(1, 2, 3) == 0) then
    