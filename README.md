contrail-packaging
==================

Contrail VNC packaging
----------------------

This is for contrail vnc packaging

build
-----
    Contains packager scripts

common
------
    Contains Makefiles, Spec files, Rules files and Control files for contrail packages

openstack
---------
    Contains Makefiles, Spec files, Rules files for contrail built openstack packages

third_party
-----------
    Contains Makefiles, Spec files for contrail built third party packages

tools
-----
    Contains ansible scripts and build tools
    
How to Package
--------------
    "packager.py" builds final debian or rpm packages based on the config files present in 
    package_configs directory. Below are examples on how packager can be triggered. Please see ./packager -h for 
    detailed help
    
    Examples:
    ./packager.py --build-id 1234 --sku havana
    
    Custom config file: 
    Packager's default can be overriden by values specified in config file or CLI. Use below option to specify 
    custom config file. By default "config" file present in current directory is used.
    ./packager.py --build-id 1234 --sku grizzly --config <config-file>
    
    Custom Store Directory: 
    Packager stores info like execution logs, packaged list in store directory. Use below option to specify 
    custom store directory. Default store directory is sandbox/build/
    ./packager.py --build-id 1234 --sku grizzly --store-dir <path-to-store-dir>
    
    Custom Third party files directory: 
    Packager picks up third party packages specified in package_configs/<OS>/<SKU>/depends_packages.cfg from 
    default cache directory. Use below option to specify custom directory from where third party packages 
    can be fetched. Separate multiple directories with space.
    ./packager.py --build-id 1234 --sku grizzly --absolute-package-dir <path/to/dir>
    ./packager.py --build-id 1234 --sku grizzly --absolute-package-dir <path/to/dir/1> <path/to/dir/2>
    
    Skip build/Reuse pre-built Contrail packages:
    Packager makes all packages by default. To reuse existing packages or to avoid making packages again, 
    use below option to specify the directory from which packages (other than third party depends packages) 
    can be fetched. Separate multiple directories with space
    ./packager.py --build-id 1234 --sku grizzly --contrail-package-dir <path/to/dir/1>
    ./packager.py --build-id 1234 --sku grizzly --contrail-package-dir <path/to/dir/1> <path/to/dir/2>
    
    Custom thirdparty depends package config file:
    Packager uses config files present in package_configs/<OS>/<SKU>/depends_packages.cfg to fetch third party packages. 
    Use below option to specify custom depends packages config file. Separate multiple files with space
    ./packager.py --build-id 1234 --sku grizzly --depends-package-file <file1>
    ./packager.py --build-id 1234 --sku grizzly --depends-package-file <file1> <file2>
    
    Custom contrail package config file:
    Packager uses config file present in package_configs/<OS>/<SKU>/contrail_packages.cfg to fetch contrail packages.
    Use below option to specify custom contrail packages config file. Separate multiple files with space.
    ./packager.py --build-id 1234 --sku grizzly --contrail-package-file <file1>
    ./packager.py --build-id 1234 --sku grizzly --contrail-package-file <file1> <file2>
    
    


