========================
Configuration
========================
Configuration can be in any file you choose however mirrors.conf is what is
included. The file must be included when mirrors is run with the -c flag. 

(ex.  mirrors -c mirrors.conf)

Global Config Options
========================

.. code-block:: python

    [DEFAULT]

All of the global configuration is stored within the [DEFAULT] block. If it is
not present the application will fail to load.

.. code-block:: python

    async_processes = 4

The number of syncs that may be run at any given time. Scheduled syncs will
wait until a spot opens up before it will begin running. 

.. code-block:: python

    log_file = ./mirrors.log

Application log file. This is were errors, warnings or general information is
logged to. Default is mirrors.log

.. code-block:: python

    check_sleep = 30

Time to sleep in between syncs . Default is 30 seconds. 

Repo Options
============
.. code-block:: python

    [test1]

Name of the repo in brackets. This is how it will be accessed within the repl.

.. code-block:: python

    source = rsync://mirrors.rit.edu/FreeBSD

Source of the rsync transfer.

.. code-block:: python

    rsync_args = -avhz

Flags to pass into the rsync process.

.. code-block:: python

    destination = ./distros/

Destination of the rsync file transfer.

.. code-block:: python

    weight = 0

Weight of the sync. Lower numbers will go before higher numbers. Value between
-10 and 10. Default is 0

.. code-block:: python

    pre_command =

Shell command to run before the rsync starts.

.. code-block:: python

    post_command =

Shell command to run after the rsync finishes.

.. code-block:: python

    log_file = ./log/LDP.log

Location of the repo log file. Rsync STDOUT and STDERR are piped here.

.. code-block:: python

    async_sleep = 2h

Time to wait after a sync has completed before it is re-queued.

.. code-block:: python

    hourly_sync = 0,6.5,12,18.5

Strict time frame for syncs to run.
