# -*- coding: UTF-8 -*-

if __name__ == '__main__':
    import sys
    sys_args = sys.argv[:]
    cmd = sys_args[1]
    if cmd == 'easy-test':
        import EasyTest
        EasyTest.easy_test()

    elif cmd == 'make-obb':
        from AsHelper import OBBMaker
        OBBMaker.make_obb()

    elif cmd == 'make-icon':
        from IconImages.ios import iOSIconMaker
        iOSIconMaker.make_icon()

    elif cmd == 'make-image':
        from IconImages.ios import iOSLaunchMaker
        iOSLaunchMaker.make_launch()

    elif cmd == 'make-obfuscate-xcodeproj':
        from XcHelper import XCProcess
        XCProcess.get_process().build_confuse()

    elif cmd == 'package-ipa':
        from XcHelper import XCProcess
        XCProcess.get_process().build_signed_ipa()

    elif cmd == 'dev2-sockserver':
        from Dev2.SockServer import SockServer
        SockServer.test()

    elif cmd.startswith('client2') :
        from Dev2.Client2 import Client2
        del sys_args[1]
        Client2(sys_args)