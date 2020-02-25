

ROS 源码解读

<https://blog.csdn.net/lewif/category_6998696.html>

# 1. roscore

原文链接：https://blog.csdn.net/lewif/article/details/75112520

```
yhzhao@yhzhao:~$ which  roscore
/opt/ros/kinetic/bin/roscore
```

roscore的源代码的git地址为`https://github.com/ros/ros_comm.git`

1. 首先是log的文件夹，log文件对阅读源代码的作用还是比较大；
2. 启动了roslunch server，url为<http://localhost:34895/>；
3. 启动了两个进程，master，pid为16195,rosout-1,pid为16208

```
yhzhao@yhzhao:~$ roscore
... logging to /home/yhzhao/.ros/log/b745073c-2ba3-11ea-96b0-98eecb94140d/roslaunch-yhzhao-16185.log
Checking log directory for disk usage. This may take awhile.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://localhost:34895/
ros_comm version 1.12.14


SUMMARY
========

PARAMETERS
 * /rosdistro: kinetic
 * /rosversion: 1.12.14

NODES

auto-starting new master
process[master]: started with pid [16195]
ROS_MASTER_URI=http://localhost:11311/

setting /run_id to b745073c-2ba3-11ea-96b0-98eecb94140d
process[rosout-1]: started with pid [16208]
started core service [/rosout]

```

roslaunch脚本只有两句话，其实是导入了roslaunch包，执行了roslaunch.main()函数，所以后续先分析roslaunch package。

```
#ros_comm\tools\roslaunch\scripts\roslaunch
import roslaunch
roslaunch.main()
```

 



# 2. roslaunch



**python distutils**

distutils可以用来在Python环境中构建和安装额外的模块。新的模块可以是纯python的，也可以是用C/C++写的扩展模块，或者可以是Python包，包中包含了由C和Python编写的模块。对于模块开发者以及需要安装模块的使用者来说，distutils的使用都很简单，作为一个开发者，除了编写源码之外，还需要：

- 编写setup脚本（一般是setup.py）；
- 编写一个setup配置文件（可选）；
- 创建一个源码发布；
- 创建一个或多个构建（二进制）发布（可选）;



setup.py

```
from distutils.core import setup

setup(name='Distutils',
      version='1.0',
      description='Python Distribution Utilities',
      author='Greg Ward',
      author_email='gward@python.net',
      url='https://www.python.org/sigs/distutils-sig/',
      packages=['distutils', 'distutils.command'],
     )

```



**roslaunch 包结构分析**

roslaunch的setup.py

```
#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['roslaunch'],
    package_dir={'': 'src'},
    scripts=['scripts/roscore',
             'scripts/roslaunch',
             'scripts/roslaunch-complete',
             'scripts/roslaunch-deps',
             'scripts/roslaunch-logs'],
    requires=['genmsg', 'genpy', 'roslib', 'rospkg']
)

setup(**d)
```

其中的catkin_pkg，其git地址为`https://github.com/ros-infrastructure/catkin_pkg.git`

<https://github.com/ros-infrastructure/catkin_pkg/blob/master/src/catkin_pkg/python_setup.py> 其核心功能就是将package.xml文件中的内容解析放到一个字典中，然后返回。

```
​`````
def generate_distutils_setup(package_xml_path=os.path.curdir, **kwargs):
    package = parse_package(package_xml_path)

    data = {}
    data['name'] = package.name
    data['version'] = package.version

    # either set one author with one email or join all in a single field
    if len(package.authors) == 1 and package.authors[0].email is not None:
        data['author'] = package.authors[0].name
        data['author_email'] = package.authors[0].email
    else:
        data['author'] = ', '.join([('%s <%s>' % (a.name, a.email) if a.email is not None else a.name) for a in package.authors])

    # either set one maintainer with one email or join all in a single field
    if len(package.maintainers) == 1:
        data['maintainer'] = package.maintainers[0].name
        data['maintainer_email'] = package.maintainers[0].email
    else:
        data['maintainer'] = ', '.join(['%s <%s>' % (m.name, m.email) for m in package.maintainers])

    # either set the first URL with the type 'website' or the first URL of any type
    websites = [url.url for url in package.urls if url.type == 'website']
    if websites:
        data['url'] = websites[0]
    elif package.urls:
        data['url'] = package.urls[0].url

    if len(package.description) <= 200:
        data['description'] = package.description
    else:
        data['description'] = package.description[:197] + '...'
        data['long_description'] = package.description

    data['license'] = ', '.join(package.licenses)
    
	#输入参数kwargs中收集的key如果在package.xml中有，则值必须一样； 如果没有，则添加到返回值中。
    # pass keyword arguments and verify equality if generated and passed in
    for k, v in kwargs.items():
        if k in data:
            if v != data[k]:
                raise InvalidPackage('The keyword argument "%s" does not match the information from package.xml: "%s" != "%s"' % (k, v, data[k]), package_xml_path)
        else:
            data[k] = v

    return data
```



package.xml中都是一些distutils中setup()函数执行时需要的一些参数，用xml进行可配置化。

```
<?xml version="1.0"?>

<package format="2">
    <name>map_manager</name>
    <version>0.0.1</version>
    <description>
        map_manager: [Feature]add map_manager for map_pack map wall point
     services:
           GetCurrentMapName.srv
           GetMapData.srv
           GetMapLists.srv
           GetMapPack.srv
           GetWallData.srv
           SaveMapPack.srv
           SetMapData.srv
           SetMapPack.srv
           SetWallData.srv
     topics:
           current_map
	   current_map_metadata

    </description>
    <author>kint.zhao</author>
    <maintainer email="zhao.yonghua@chinaredstar.cn">kint.zhao</maintainer>
    <url>http://wiki.ros.org/map_server</url>
    <license>BSD</license>

    <buildtool_depend version_gte="0.5.68">catkin</buildtool_depend>

    <depend>bullet</depend>
    <depend>nav_msgs</depend>
    <depend>roscpp</depend>
    <depend>roslib</depend>
    <depend>sdl</depend>
    <depend>sdl-image</depend>
    <depend>yaml-cpp</depend>
    <depend>yunshen_robot_msgs</depend>
    <depend>yunshen_robot_data_persistence</depend>

</package>
```



**python 模块主要是用来被其他模块去import，而script是为了直接在命令行执行**



roscore最终会去import roslaunch package，去调用其中的main函数。

```
#ros_comm\tools\roslaunch\scripts\roscore
import roslaunch
roslaunch.main(['roscore', '--core'] + sys.argv[1:])
```



# 3 rosmaster

原文链接：https://blog.csdn.net/lewif/article/details/75174123

* 3.1 rosmaster包下的setup.py

```
#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['rosmaster'],
    package_dir={'': 'src'},
    scripts=['scripts/rosmaster'],
    requires=['roslib', 'rospkg']
)

setup(**d)
```

* 3.2 scripts/rosmaster

```
import rosmaster
rosmaster.rosmaster_main()
```

`rosmaster/__init__.py`

```
from .main import rosmaster_main
from .master import DEFAULT_MASTER_PORT
```

1 ==>>>   `rosmaster/main.py`

```
def rosmaster_main(argv=sys.argv, stdout=sys.stdout, env=os.environ):
     #①前面都是解析命令行参数
    parser = optparse.OptionParser(usage="usage: zenmaster [options]")
    parser.add_option("--core",
                      dest="core", action="store_true", default=False,
                      help="run as core")
    parser.add_option("-p", "--port", 
                      dest="port", default=0,
                      help="override port", metavar="PORT")
    parser.add_option("-w", "--numworkers",
                      dest="num_workers", default=NUM_WORKERS, type=int,
                      help="override number of worker threads", metavar="NUM_WORKERS")
    parser.add_option("-t", "--timeout",
                      dest="timeout",
                      help="override the socket connection timeout (in seconds).", metavar="TIMEOUT")
    options, args = parser.parse_args(argv[1:])

    # only arg that zenmaster supports is __log remapping of logfilename
    for arg in args:
        if not arg.startswith('__log:='):
            parser.error("unrecognized arg: %s"%arg)
    configure_logging()   
    
    # ②rosmaster进程默认监听端关于python xmlrpc口   
    port = rosmaster.master.DEFAULT_MASTER_PORT
    if options.port:
        port = int(options.port)

    if not options.core:
        print(""" ``````""")

    logger = logging.getLogger("rosmaster.main")
    logger.info("initialization complete, waiting for shutdown")
关于python xmlrpc
    if options.timeout is not None and float(options.timeout) >= 0.0:
        logger.info("Setting socket timeout to %s" % options.timeout)
        import socket
        socket.setdefaulttimeout(float(options.timeout))

    try:
        logger.info("Starting ROS Master Node")
         #③ 创建Master对象，启动XmlRpcNode
         #number of threads we use to send publisher_update notifications
        master = rosmaster.master.Master(port, options.num_workers)
        master.start()

        import time
        while master.ok():
            time.sleep(.1)
    except KeyboardInterrupt:
        logger.info("keyboard interrupt, will exit")
    finally:
        logger.info("stopping master...")
        master.stop()
```

上段代码最重要的是第③部分：
 创建了个Master类对象，默认端口为11311 ，三个工作线程； 调用start()。

2 ==>>>   `rosmaster/main.py`

```
DEFAULT_MASTER_PORT=11311 #default port for master's to bind to
```



* 3.3 关于python xmlrpc
  <https://www.cnblogs.com/wanghaoran/p/3189017.html>
  XML-RPC（Remote Procedure Call）是通过HTTP传输协议，利用XML格式的远端程序调用方法。客户端可以调用服务端带参数的方法并获取返回的结构数据。（服务端的名字是一个URI）。这个模块支持写入XML-RPC端的代码。它用来处理所有转换的细节在在整合的Python对象和XML报文之间。

  

* 3.4 rosmaster/master.py

  ```
  import rosgraph.xmlrpc
  import rosmaster.master_api
  
  class Master(object):
      
      def __init__(self, port=DEFAULT_MASTER_PORT, num_workers=rosmaster.master_api.NUM_WORKERS):
          self.port = port
          self.num_workers = num_workers
          
      def start(self):
          """
          Start the ROS Master.
          """
          self.handler = None
          self.master_node = None
          self.uri = None
          
          #① 创建一个class ROSMasterHandler(object)对象
          handler = rosmaster.master_api.ROSMasterHandler(self.num_workers)
           #② 创建一个XmlRpcNode对象
          master_node = rosgraph.xmlrpc.XmlRpcNode(self.port, handler)
          #③ 调用XmlRpcNode的start(),其实是新启动一个线程，线程函数为XmlRpcNode中的run()
          master_node.start()
  
          # poll for initialization
          while not master_node.uri:
              time.sleep(0.0001) 
  
          # save fields
          self.handler = handler
          self.master_node = master_node
          self.uri = master_node.uri
          
          logging.getLogger('rosmaster.master').info("Master initialized: port[%s], uri[%s]", self.port, self.uri)
  
      def ok(self):
          if self.master_node is not None:
              return self.master_node.handler._ok()
          else:
              return False
      
      def stop(self):
          if self.master_node is not None:
              self.master_node.shutdown('Master.stop')
              self.master_node = None
  
  ```

  

* 3.5 `import rosmaster.master_api` ==>  rosmaster/master_api.py

  ```
  # Master Implementation
  class ROSMasterHandler(object):
      """
      XML-RPC handler for ROS master APIs.
      """
      
      def __init__(self, num_workers=NUM_WORKERS):
          """ctor."""
  
          self.uri = None
          self.done = False
  
          self.thread_pool = rosmaster.threadpool.MarkedThreadPool(num_workers)
          # pub/sub/providers: dict { topicName : [publishers/subscribers names] }
          self.ps_lock = threading.Condition(threading.Lock())
  
          self.reg_manager = RegistrationManager(self.thread_pool)
  
          # maintain refs to reg_manager fields
          self.publishers  = self.reg_manager.publishers
          self.subscribers = self.reg_manager.subscribers
          self.services = self.reg_manager.services
          self.param_subscribers = self.reg_manager.param_subscribers
          
          self.topics_types = {} #dict { topicName : type }
  
          # parameter server dictionary
          self.param_server = rosmaster.paramserver.ParamDictionary(self.reg_manager)
  ```

* 3. 6`import rosgraph.xmlrpc` ==>  rosgraph/xmlrpc.py

     ```
     from __future__ import print_function
     
     class SilenceableXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
     class ThreadingXMLRPCServer(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
     class ForkingXMLRPCServer(socketserver.ForkingMixIn, SimpleXMLRPCServer):
     class XmlRpcHandler(object):
     
     class XmlRpcNode(object):
         """
         Generic XML-RPC node. Handles the additional complexity of binding
         an XML-RPC server to an arbitrary port. 
         XmlRpcNode is initialized when the uri field has a value.
         """
     
         def __init__(self, port=0, rpc_handler=None, on_run_error=None):
             #XML RPC Node constructor 调用父类构造函数
             super(XmlRpcNode, self).__init__()
            
             #①构造函数传进来的rpc_handler
             self.handler = rpc_handler
             self.uri = None # initialize the property now so it can be tested against, will be filled in later
             self.server = None
             if port and isstring(port):
                 port = int(port)
             self.port = port
             self.is_shutdown = False
             self.on_run_error = on_run_error
     
         def shutdown(self, reason):
             """
             Terminate i/o connections for this server.
     
             :param reason: human-readable debug string, ``str``
             """
             self.is_shutdown = True
             if self.server:
                 server = self.server
                 handler = self.handler
                 self.handler = self.server = self.port = self.uri = None
                 if handler:
                     handler._shutdown(reason)
                 if server:
                     server.socket.close()
                     server.server_close()
                     
         def start(self):
             """
             Initiate a thread to run the XML RPC server. Uses thread.start_new_thread.
             """
              #② 启动新线程，线程函数为run()
             _thread.start_new_thread(self.run, ())
     
         def set_uri(self, uri):
             """
             Sets the XML-RPC URI. Defined as a separate method as a hood
             for subclasses to bootstrap initialization. Should not be called externally.
     
             :param uri: XMLRPC URI, ``str``
             """
             self.uri = uri
             
         def run(self):
             try:
                 self._run()
             except Exception as e:
                 if self.is_shutdown:
                     pass
                 elif self.on_run_error is not None:
                    self.on_run_error(e)
                 else:
                     raise
     
         # separated out for easier testing
         def _run_init(self):
             logger = logging.getLogger('xmlrpc')            
             try:
                 log_requests = 0
                 port = self.port or 0 #0 = any
     
                 bind_address = rosgraph.network.get_bind_address()
                 logger.info("XML-RPC server binding to %s:%d" % (bind_address, port))
                 
                 self.server = ThreadingXMLRPCServer((bind_address, port), log_requests)
                 self.port = self.server.server_address[1] #set the port to whatever server bound to
                 if not self.port:
                     self.port = self.server.socket.getsockname()[1] #Python 2.4
     
                 assert self.port, "Unable to retrieve local address binding"
     
                 # #528: semi-complicated logic for determining XML-RPC URI
                 # - if ROS_IP/ROS_HOSTNAME is set, use that address
                 # - if the hostname returns a non-localhost value, use that
                 # - use whatever rosgraph.network.get_local_address() returns
                 uri = None
                 override = rosgraph.network.get_address_override()
                 if override:
                     uri = 'http://%s:%s/'%(override, self.port)
                 else:
                     try:
                         hostname = socket.gethostname()
                         if hostname and not hostname == 'localhost' and not hostname.startswith('127.') and hostname != '::':
                             uri = 'http://%s:%s/'%(hostname, self.port)
                     except:
                         pass
                 if not uri:
                     uri = 'http://%s:%s/'%(rosgraph.network.get_local_address(), self.port)
                 self.set_uri(uri)
                 
                 logger.info("Started XML-RPC server [%s]", self.uri)
                 
                 # ③这里最主要的是下面两个函数，将handler注册到xml-rpc 
                 self.server.register_multicall_functions()
                 self.server.register_instance(self.handler)
     
             except socket.error as e:
                 if e.errno == 98:
                     msg = "ERROR: Unable to start XML-RPC server, port %s is already in use"%self.port
                 else:
                     msg = "ERROR: Unable to start XML-RPC server: %s" % e.strerror
                 logger.error(msg)
                 print(msg)
                 raise #let higher level catch this
     
             if self.handler is not None:
                 self.handler._ready(self.uri)
             logger.info("xml rpc node: starting XML-RPC server")
             
         def _run(self):
             """
             Main processing thread body.
             :raises: :exc:`socket.error` If server cannot bind
             
             """
             self._run_init()
             while not self.is_shutdown:
                 try:
                     #④ 服务端开始监听运行
                     self.server.serve_forever()
                 except (IOError, select.error) as e:
                     # check for interrupted call, which can occur if we're
                     # embedded in a program using signals.  All other
                     # exceptions break _run.
                     if self.is_shutdown:
                         pass
                     elif e.errno != 4:
                         self.is_shutdown = True
                         logging.getLogger('xmlrpc').error("serve forever IOError: %s, %s"%(e.errno, e.strerror))
                         
     
     ```

     

通过上面的代码分析可以看到rosmaster的整个执行流程：
rosmaster命令行脚本执行rosmaster_main()；
启动了一个新的线程来启动xml-rpc server(rosmaster)；
xml-rpc server注册了一个类为ROSMasterHandler，定义了rpc的方法。 

# 4. roslaunch之process monitoring(pmon)

<https://blog.csdn.net/lewif/article/details/75212571>

roslaunch/pmon.py
roslaunch中有个小功能类似于android init进程中的service重启功能，如果该进程在创建时有respawn属性，则在该进程dead后需要将其重启起来，起到一个进程监控的作用，相关源码位于pmon.py。

```
class Process(object):
    def __init__(self, package, name, args, env,
            respawn=False, respawn_delay=0.0, required=False):
        self.package = package
        self.name = name
        self.args = args
        self.env = env
 #①进程的属性，respawn为是否需要重启    
        self.respawn = respawn
        self.respawn_delay = respawn_delay
        self.required = required
        self.lock = Lock()
        self.exit_code = None
        # for keeping track of respawning
        self.spawn_count = 0
        self.time_of_death = None

        _init_signal_handlers()
```

Process()类就是ProcessMonitor()所监控的进程需要去继承的基类，可以设置dead后是否需要重启属性。

通过调用`start_process_monitor()`函数可以启动一个ProcessMonitor进程(线程)，

```
#① 可以有多个pmon
_pmons = []
_pmon_counter = 0
def start_process_monitor():
    global _pmon_counter
    if _shutting_down:
        #logger.error("start_process_monitor: cannot start new ProcessMonitor (shutdown initiated)")
        return None
    _pmon_counter += 1
    name = "ProcessMonitor-%s"%_pmon_counter
    logger.info("start_process_monitor: creating ProcessMonitor")
    
#②创建ProcessMonitor对象
    process_monitor = ProcessMonitor(name)
    try:
        # prevent race condition with pmon_shutdown() being triggered
        # as we are starting a ProcessMonitor (i.e. user hits ctrl-C
        # during startup)
        _shutdown_lock.acquire()
#③将ProcessMonitor对象添加到_pmons中，并调用其start()函数
        _pmons.append(process_monitor)
        process_monitor.start()
        logger.info("start_process_monitor: ProcessMonitor started")
    finally:
        _shutdown_lock.release()

    return process_monitor
```



```
class ProcessMonitor(Thread):

    def __init__(self, name="ProcessMonitor"):
        Thread.__init__(self, name=name)
         # ①所监控的进程
        self.procs = []
        self.plock = RLock()
        self.is_shutdown = False
        self.done = False        
        self.setDaemon(True)
        self.reacquire_signals = set()
        self.listeners = []
        self.dead_list = []
        # #885: ensure core procs
        self.core_procs = []
        # #642: flag to prevent process monitor exiting prematurely
        self._registrations_complete = False
        
        logger.info("created process monitor %s"%self)
 
    def register(self, p):
        logger.info("ProcessMonitor.register[%s]"%p.name)
        e = None
        with self.plock:
            if self.has_process(p.name):
                e = RLException("cannot add process with duplicate name '%s'"%p.name)
            elif self.is_shutdown:
                e = RLException("cannot add process [%s] "%p.name)
            else:
 #② 将进程注册到ProcessMonitor，即添加到procs 
                self.procs.append(p)
        if e:
            logger.error("ProcessMonitor.register[%s] failed %s"%(p.name, e))
            raise e
        else:
            logger.info("ProcessMonitor.register[%s] complete"%p.name)
 
 #③ProcessMonitor线程的线程函数
    def run(self):
        try:
            #don't let exceptions bomb thread, interferes with exit
            try:
                self._run()
            except:
                logger.error(traceback.format_exc())
                traceback.print_exc()
        finally:
            self._post_run()
            
  #④ProcessMonitor线程的线程函数的主体    
    def _run(self):
        """
        Internal run loop of ProcessMonitor
        """
        plock = self.plock
        dead = []
        respawn = []
        #while循环，pmon关闭开关
        while not self.is_shutdown:
            with plock: #copy self.procs
                procs = self.procs[:]
            if self.is_shutdown:
                break

            for s in _signal_list:
                if signal.getsignal(s) !=  rl_signal:
                    self.reacquire_signals.add(s)
#监控中的进程
            for p in procs:
                try:
                    if not p.is_alive():
                        exit_code_str = p.get_exit_description()
                        if p.required:
                            self.is_shutdown = True
                        elif not p in respawn:
                            if p.exit_code:
                                printerrlog("[%s] %s"%(p.name, exit_code_str))
                            else:
                                printlog_bold("[%s] %s"%(p.name, exit_code_str))
                            dead.append(p)
                            
                        ## no need for lock as we require listeners be
                        ## added before process monitor is launched
                        for l in self.listeners:
                            l.process_died(p.name, p.exit_code)

                except Exception as e:
                    traceback.print_exc()
                    #don't respawn as this is an internal error
                    dead.append(p)
                if self.is_shutdown:
                    break #stop polling
            for d in dead:
                try:
                    if d.should_respawn():
                        respawn.append(d)
                    else:
                        self.unregister(d)
                        # stop process, don't accumulate errors
                        d.stop([])
                        # save process data to dead list
                        with plock:
                            self.dead_list.append(DeadProcess(d))
                except:
                    logger.error(traceback.format_exc())
                    
            # dead check is to make sure that ProcessMonitor at least
            # waits until its had at least one process before exiting
            if self._registrations_complete and dead and not self.procs and not respawn:
                printlog("all processes on machine have died, roslaunch will exit")
                self.is_shutdown = True
            del dead[:]
            _respawn=[]
            for r in respawn: 
                try:
                    if self.is_shutdown:
                        break
                    if r.should_respawn() <= 0.0:
                        printlog("[%s] restarting process" % r.name)
                        # stop process, don't accumulate errors
                         #⑥ 重启需要重启的进程，起到进程监控的作用。
                        r.stop([])
                        r.start()
                    else:
                        # not ready yet, keep it around
                        _respawn.append(r)
                except:
                    traceback.print_exc()
                    logger.error("Restart failed %s",traceback.format_exc())
            respawn = _respawn
            time.sleep(0.1) #yield thread
        #moved this to finally block of _post_run
        #self._post_run() #kill all processes

```



通过上面代码发现，self.is_shutdown是pmon的关闭开关，当is_shutdown为True，则while循环退出，将会继续执行_post_run()，会杀掉所有的监控进程，不过有顺序，最后杀掉核心进程(core_procs)。

```
    def _post_run(self):
        logger.info("ProcessMonitor._post_run %s"%self)
        # this is already true entering, but go ahead and make sure
        self.is_shutdown = True
        # killall processes on run exit

        q = Queue()
        q.join()
        
        with self.plock:
            # make copy of core_procs for threadsafe usage
            core_procs = self.core_procs[:]
            logger.info("ProcessMonitor._post_run %s: remaining procs are %s"%(self, self.procs))

            # enqueue all non-core procs in reverse order for parallel kill
            # #526/885: ignore core procs
            [q.put(p) for p in reversed(self.procs) if not p in core_procs]

        # use 10 workers
        killers = []
        for i in range(10):
            t = _ProcessKiller(q, i)
            killers.append(t)
            t.start()

        # wait for workers to finish
        q.join()
        shutdown_errors = []

        # accumulate all the shutdown errors
        for t in killers:
            shutdown_errors.extend(t.errors)
        del killers[:]
            
        # #526/885: kill core procs last
        # we don't want to parallelize this as the master has to be last
        for p in reversed(core_procs):
            _kill_process(p, shutdown_errors)

        # delete everything except dead_list
        logger.info("ProcessMonitor exit: cleaning up data structures and signals")
        with self.plock:
            del core_procs[:]
            del self.procs[:]
            del self.core_procs[:]
            
        reacquire_signals = self.reacquire_signals
        if reacquire_signals:
            reacquire_signals.clear() 
        logger.info("ProcessMonitor exit: pmon has shutdown")
        self.done = True

        if shutdown_errors:
            printerrlog("Shutdown errors:\n"+'\n'.join([" * %s"%e for e in shutdown_errors]))


```

**通过pmon.py的代码分析，pmon.py肯定是在一个进程的主线程中去import，调用start_process_monitor()函数就会产生一个pmon，然后把需要监控的进程(线程)注册到pmon中，主线程会有多个pmon保存在全局_pmons = []中。**



# 5. rosmaster xmlrpc api

大部分的package不需要直接与rosmaster交互, rosmaster在roscore启动时自动启动, 大部分程序通过XMLRPC APIs与roscore进行通讯

 * Using XMLRPC

The Master API is implemented via XMLRPC, which has good library support in a variety of languages. For example, in Python:

```
import os
import xmlrpclib
caller_id = '/script'
m = xmlrpclib.ServerProxy(os.environ['ROS_MASTER_URI'])
#调用getSystemState api
code, msg, val = m.getSystemState(caller_id)
if code == 1:
  pubs, subs, srvs = val
else:
  print "call failed", code, msg
```



# API Listing

* ### **register/unregister methods**

**registerService(caller_id, service, service_api, caller_api)**

**unregisterService(caller_id, service, service_api)**

**registerSubscriber(caller_id, topic, topic_type, caller_api)**

**unregisterSubscriber(caller_id, topic, caller_api)**

**registerPublisher(caller_id, topic, topic_type, caller_api)**

**unregisterPublisher(caller_id, topic, caller_api)**

* ### Name service and system state

**lookupNode(caller_id, node_name)**

**getPublishedTopics(caller_id, subgraph)**

**getTopicTypes(caller_id)**

**getSystemState(caller_id)**

**getUri(caller_id)**

**lookupService(caller_id, service)**

























