function test_getframe()
    mmwsViewer();
    f = gcf;
    pause(1);
    F = getframe(f);
    imwrite(F.cdata, 'mockup_getframe.png');
    exit;
end
