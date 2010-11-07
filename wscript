# -*- mode: python -*-

APPNAME='eventmachine'
VERSION='0.12.10'

import sys

top = '.'
out = 'build'

def options(opt):
    opt.load('compiler_cxx')
    opt.add_option('--without-ssl', action='store_true',
                   help='Do not use ssl, even if available')
    opt.add_option('--with-ssl', action='store_true',
                   help='Fail if ssl is not available')
    opt.add_option('--no-shlib', action='store_true',
                   help='Do not build a shared library')
    opt.add_option('--no-stlib', action='store_true',
                   help='Do not build a static library')

def configure(cfg):
    cfg.load('compiler_cxx')
    cfg.check_library()

    try: cfg.check(header_name='sys/inotify.h', function_name='inotify_init',
                   define_name='HAVE_INOTIFY')
    except: pass

    try: cfg.check(header_name='sys/uio.h', function_name='writev',
                   define_name='HAVE_WRITEV')
    except: pass

    if sys.platform == 'win32' or sys.platform == 'cygwin':
        cfg.define('OS_WIN32', 1)
    else:
        cfg.define('OS_UNIX', 1)

    try:
        cfg.check(header_name='sys/event.h')
        cfg.check(header_name='sys/queue.h')
        cfg.define('HAVE_KQUEUE', 1)
    except: pass

    try: cfg.check(header_name='sys/epoll.h', function_name='epoll_create',
                   define_name='HAVE_EPOLL')
    except: pass

    try: cfg.check(fragment='''
                     #include <utility>
                     using namespace std;
                     int main(){ pair<int,int> tuple = make_pair(1,2); }''',
                   define_name='HAVE_MAKE_PAIR', msg='Checking for std::pair')
    except: pass

    try:
        if cfg.options.without_ssl:
            cfg.fatal('--with-ssl and --without-ssl specified at the same time')

        cfg.check_cfg(package='openssl', args=['--cflags', '--libs'])
        cfg.define('WITH_SSL', 1)
    except:
        if cfg.options.with_ssl: raise
        cfg.define('WITHOUT_SSL', 1)

    cfg.env['BUILD_STLIB'] = not cfg.options.no_stlib
    cfg.env['BUILD_SHLIB'] = not cfg.options.no_shlib

    cfg.write_config_header('eventmachine_config.h')

def build(bld):
    src = [ 'ext/binder.cpp',
            'ext/cmain.cpp',
            'ext/cplusplus.cpp',
            'ext/ed.cpp',
            'ext/em.cpp',
            'ext/emwin.cpp',
            'ext/epoll.cpp',
            'ext/files.cpp',
            'ext/kb.cpp',
            'ext/page.cpp',
            'ext/pipe.cpp',
            'ext/sigs.cpp',
            'ext/ssl.cpp' ]
    headers = [ 'ext/binder.h',
                'ext/ed.h',
                'ext/em.h',
                'ext/emwin.h',
                'ext/epoll.h',
                'ext/eventmachine_cpp.h',
                'ext/eventmachine.h',
                'ext/files.h',
                'ext/page.h',
                'ext/project.h',
                'ext/sigs.h',
                'ext/ssl.h',
                'eventmachine_config.h' ]

    if bld.env.BUILD_STLIB:
        bld.stlib(source   = src,
                  target   = 'eventmachine',
                  includes = '.',
                  use      = 'OPENSSL')

    if bld.env.BUILD_SHLIB:
        bld.shlib(source   = src,
                  target   = 'eventmachine',
                  includes = '.',
                  use      = 'OPENSSL',
                  vnum     = VERSION )

    bld.install_files('${PREFIX}/include/eventmachine', headers)
