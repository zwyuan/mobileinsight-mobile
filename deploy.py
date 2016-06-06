#!/usr/bin/python
# Filename: deploy.py

'''
deploy.py

It deploys compiling environment and parameters for mobileInsight.

Authors : Zengwen Yuan
          Kainan Wang
Version : 2.1 -- 2015/05/16 reformat building commands
          2.2 -- 2015/05/17 add config commands to copy libs
'''

import os, sys, commands, yaml


def run_config():
    # commands.getstatusoutput('wget --no-check-certificate https://wing1.cs.ucla.edu/gitlab/zyuan/mobile-insight-libs/repository/archive.zip\?ref\=master master.zip')
    os.system('git clone https://wing1.cs.ucla.edu/gitlab/zyuan/mobile-insight-libs.git')
    if os.path.isdir('./demo_app/data') is False:
        os.makedirs('./demo_app/data')
    os.system('cp mobile-insight-libs/lib/* ./demo_app/data')
    os.system('cp mobile-insight-libs/bin/* ./demo_app/data')
    os.system('rm -rf mobile-insight-libs')
    if os.path.isfile('./config/config.yml') is True:
        os.system('cp ./config/config.yml ./config/config.yml.bak')
    os.system('tail -n+8 ./config/config_template.yml > ./config/config.yml')
    print 'Edit ./config/config.yml to set up the configuration'


def run_dist():
    build_dist_cmd = 'python-for-android create' \
            + ' --dist-name={}'.format(cfg['dist_name']) \
            + ' --bootstrap={}'.format(cfg['bootstrap']) \
            + ' --storage-dir={}'.format(cfg['p4a_path']) \
            + ' --sdk-dir={}'.format(cfg['sdk_path']) \
            + ' --android-api={}'.format(cfg['api_level']) \
            + ' --minsdk={}'.format(cfg['minsdk']) \
            + ' --ndk-dir={}'.format(cfg['ndk_path']) \
            + ' --ndk-version={}'.format(cfg['ndk_version']) \
            + ' --arch={}'.format(cfg['arch']) \
            + ' --requirements={}'.format(cfg['requirements'])

    print build_dist_cmd
    os.system(build_dist_cmd)


def run_apk(build_release):
    build_cmd = 'python-for-android apk' \
            + ' --compile-pyo' \
            + ' --copy-libs' \
            + ' --name={}'.format(cfg['app_name']) \
            + ' --dist-name={}'.format(cfg['dist_name']) \
            + ' --storage-dir={}'.format(cfg['p4a_path']) \
            + ' --version={}'.format(cfg['app_version']) \
            + ' --private={}/{}'.format(cfg['mi_dev_path'], cfg['app_path']) \
            + ' --package={}'.format(cfg['pkg_name']) \
            + ' --icon={}/{}'.format(cfg['mi_dev_path'], cfg['icon_path']) \
            + ' --presplash={}/{}'.format(cfg['mi_dev_path'], cfg['presplash_path']) \
            + ' --orientation={}'.format(cfg['orientation']) \
            + ' --sdk-dir={}'.format(cfg['sdk_path']) \
            + ' --android-api={}'.format(cfg['api_level']) \
            + ' --minsdk={}'.format(cfg['minsdk']) \
            + ' --ndk-dir={}'.format(cfg['ndk_path']) \
            + ' --ndk-version={}'.format(cfg['ndk_version']) \
            + ' --arch={}'.format(cfg['arch']) \
            + ' --whitelist={}/{}'.format(cfg['mi_dev_path'], cfg['whitelist']) \
            + ' --permission WRITE_EXTERNAL_STORAGE' \
            + ' --permission INTERNET' \
            + ' --permission RECEIVE_BOOT_COMPLETED' \
            # + ' --intent-filters BOOT_COMPLETED'

    if build_release is True:
        # This should work but currently has bug
        # build_cmd = build_cmd + ' --release' \
        #         + ' --keystore=' + str(cfg['keystore']) \
        #         + ' --signkey=' + str(cfg['signkey']) \
        #         + ' --keystorepw=' + str(cfg['keystorepw']) \
        #         + ' --signkeypw=' + str(cfg['signkeypw'])

        rm_cmd = 'rm {}-{}.apk'.format(cfg['app_name'], cfg['app_version'])
        build_cmd = build_cmd + ' --release'
        sign_cmd = 'jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1' \
            + ' -keystore {keystore} {p4a}/dists/{dist}/bin/{app}-{ver}-release-unsigned.apk {key}'.format(
            keystore=cfg['keystore'],
            p4a=cfg['p4a_path'],
            dist=cfg['dist_name'],
            app=cfg['app_name'],
            ver=cfg['app_version'],
            key=cfg['signkey'])

        zipalign_path = ""
        for subdir, dirs, files in os.walk(os.path.join(cfg['sdk_path'], 'build-tools')):
             for f in files:
                 if f == "zipalign":
                     zipalign_path = os.path.join(subdir, f)
                     break;

        align_cmd = '{zipalign} -v 4 {p4a}/dists/{dist}/bin/{app}-{ver}-release-unsigned.apk {app}-{ver}.apk'.format(
            zipalign=zipalign_path,
            p4a=cfg['p4a_path'],
            dist=cfg['dist_name'],
            app=cfg['app_name'],
            ver=cfg['app_version'])

        os.system(rm_cmd)
        os.system(build_cmd)
        os.system(sign_cmd)
        os.system(align_cmd)

        print "build command was: \n" + build_cmd
        print "sign command was: \n" + sign_cmd
        print "align command was: \n" + align_cmd
    else:
        os.system(build_cmd)
        print "build command was: \n" + build_cmd


if __name__ == '__main__':
    arg = sys.argv[1]

    try:
        debug = sys.argv[2]
    except:
        debug = ""

    try:
        with open("./config/config.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
    except:
        print "Compilation environment is not configured!\nRunning make config automatically for you..."
        run_config()
        sys.exit()

    if arg == 'config':
        run_config()
    elif arg == 'dist':
        run_dist()
    elif arg == 'apk':
        if debug == "debug" or debug == "":
            run_apk(False)
        elif debug == "release":
            run_apk(True)
        else:
            print "Usage: python deploy.py apk [debug|release]"
    elif arg == 'clean':
        for subdir, dirs, files in os.walk('.'):
            for f in files:
                if f.endswith(".pyo") or f.endswith(".DS_Store"):
                    filepath = os.path.join(subdir, f)
                    os.remove(filepath)
    elif arg == 'clean_apk':
        try:
            os.remove('{path}/{app}-{ver}.apk'.format(path=cfg['mi_dev_path'], app=cfg['app_name'], ver=cfg['app_version']))
            os.remove('{path}/{app}-{ver}-debug.apk'.format(path=cfg['mi_dev_path'], app=cfg['app_name'], ver=cfg['app_version']))
        except:
            print "APK clean failed."
    elif arg == 'clean_dist':
        try:
            os.system('rm -rf ' + os.path.join(cfg['p4a_path'], 'dists', cfg['dist_name']))
            os.system('rm -rf ' + os.path.join(cfg['p4a_path'], 'build/aars', cfg['dist_name']))
            os.system('rm -rf ' + os.path.join(cfg['p4a_path'], 'build/javaclasses', cfg['dist_name']))
            os.system('rm -rf ' + os.path.join(cfg['p4a_path'], 'build/libs_collections', cfg['dist_name']))
            os.system('rm -rf ' + os.path.join(cfg['p4a_path'], 'build/python-installs', cfg['dist_name']))
            os.system('p4a clean_dists')
            print "Dist %s successfully cleaned." % cfg['dist_name']
        except:
            print "Dist %s clean failed."
    elif arg == 'clean_all':
        try:
            os.system('p4a clean_all')
            os.system('p4a clean_builds')
            os.system('p4a clean_dists')
            os.system('p4a clean_download_cache')
        except:
            pass
    elif arg == 'install':
        try:
            os.system('adb install -r {app}-{ver}.apk'.format(app=cfg['app_name'], ver=cfg['app_version']))
        except:
            os.system('adb install -r {app}-{ver}-debug.apk'.format(app=cfg['app_name'], ver=cfg['app_version']))
    elif arg == 'update':
        try:
            if debug == 'icellular':
                os.system('adb shell "rm -r /sdcard/mobile_insight/apps/iCellular/"')
                os.system('adb push ./internal_app/iCellular/ /sdcard/mobile_insight/apps/iCellular/')
            elif debug == 'netlogger':
                os.system('adb shell "rm -r /sdcard/mobile_insight/apps/NetLoggerInternal/"')
                os.system('adb push ./internal_app/NetLoggerInternal/ /sdcard/mobile_insight/apps/NetLoggerInternal/')
        except:
            print "Sorry, your arguments are not supported for this moment."