function save_mock()
    mmwsViewer();
    f = gcf;
    exportgraphics(f, 'mockup.png', 'Resolution', 150);
    exit;
end
