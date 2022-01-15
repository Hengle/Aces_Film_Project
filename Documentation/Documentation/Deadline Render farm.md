# Deadline Renderfarm


This is where I will start putting documentation for the renderfarm at UVU.

---
# repository
- a separate machine
- stores configuration
- sends files to other machines


https://www.youtube.com/watch?v=v083eMXSwXw
https://timvanhelsdingen.com/vfx-folderstructure/

$JOB is important for using the render farm

make deadline work with a different houdini version

custom deadline entry for houdini
houdini plugin and env vars on each machine


---
- Render farm
	- Amazon account
	- Update deadline
	- https://docs.thinkboxsoftware.com/products/deadline/10.1/1_User%20Manual/manual/app-houdini.html#app-houdini-integrated-submission-script-label
		- Houdini integrated submission script setup
		- HQueue??
		- https://www.awsthinkbox.com/blog/common-render-farm-errors common errors
		- how to start workers??
		- startup machines if they are off??
		- Hserver?
		- update blender
		- set up client machines for job submission
		- ACES color management
		- local houdini env file needs deadline path
		- Any way to remote in from linux?
		
```
HOUDINI_MENU_PATH = "$HOUDINI_MENU_PATH;c:/Users/<user>/AppData/Deadline10/submitters/HoudiniSubmitter;&"
```

https://www.youtube.com/watch?v=v083eMXSwXw


---

! Apparently nothing should have changed licensing-wise if we have floating licenses?

! Push for redshift !

---
## Upgrading The Farm

https://www.awsthinkbox.com/blog/deadline-auto-upgrade-system



---

https://www.youtube.com/watch?v=v083eMXSwXw

## IT Tasks
- [ ] install Houdini 18.5 python2.7 on TC-render
- [ ] update blender on all machines
	- cycles-x ( much faster )
	- Eevee
- [ ] ACES on all machines https://github.com/imageworks/OpenColorIO-Configs 
	- simlink from server
	- OCIO= path to 1.03 config
- [ ] Fusion/Davinci resolve installed
- [ ] Houdini env file entry for deadline plugin 
- [ ] Houdini deadline plugin (simulations)
- [ ] Blender deadline plugin
- [ ] fix plugin errors on client machines

---

## Other IT things
- jetbrains license server?
- .NET CORE SDK not found in PATH
- install resolve/fusion
- 


---

https://forums.thinkboxsoftware.com/t/houdini-17-support/24131 



- tried to remote start worker and got this error   

A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond. 161.28.108.139:53041

---

# Important things to explain to teachers

- Deadline will help with VFX and simulations
- We can use Deadline with Harmony
- Can be used for compositing


---

If you’ve already done that, I’d expect the next issue to be with the DEADLINE_PATH environment variable not being set properly - that’s how the submitter finds where Deadline is installed on the machine. Make sure that that’s set to the /bin folder in your local install.

---


https://gpuopen.com/learn/amd-usd-hydra-blender/

---

```
  

=======================================================

Error

=======================================================

Error: Houdini 18_0 hython executable was not found in the semicolon separated list "C:\Program Files\Side Effects Software\Houdini 18.0.000\bin\Hython.exe;/Applications/Houdini/Houdini18.0.000/Frameworks/Houdini.framework/Versions/18.0.000/Resources/bin/hython;/opt/hfs18.0/bin/hython". The path to the render executable can be configured from the Plugin Configuration in the Deadline Monitor.

at Deadline.Plugins.PluginWrapper.RenderTasks(String taskId, Int32 startFrame, Int32 endFrame, String& outMessage, AbortLevel& abortLevel)

  

=======================================================

Type

=======================================================

RenderPluginException

  

=======================================================

Stack Trace

=======================================================

at Deadline.Plugins.SandboxedPlugin.d(DeadlineMessage bbr, CancellationToken bbs)

at Deadline.Plugins.SandboxedPlugin.RenderTask(String taskId, Int32 startFrame, Int32 endFrame, CancellationToken cancellationToken)

at Deadline.Slaves.SlaveRenderThread.c(TaskLogWriter adz, CancellationToken aea)

  

=======================================================

Log

=======================================================

2022-01-13 16:33:14: 0: Loading Job's Plugin timeout is Disabled

2022-01-13 16:33:16: 0: Executing plugin command of type 'Sync Files for Job'

2022-01-13 16:33:16: 0: All job files are already synchronized

2022-01-13 16:33:16: 0: Plugin Houdini was already synchronized.

2022-01-13 16:33:16: 0: Done executing plugin command of type 'Sync Files for Job'

2022-01-13 16:33:16: 0: Executing plugin command of type 'Initialize Plugin'

2022-01-13 16:33:17: 0: INFO: Executing plugin script 'C:\Users\10923227\AppData\Local\Thinkbox\Deadline10\slave\CS514-021\plugins\61e0b63e4ab1d10d404985b3\Houdini.py'

2022-01-13 16:33:17: 0: INFO: About: Houdini Plugin for Deadline

2022-01-13 16:33:17: 0: INFO: Render Job As User disabled, running as current user '10923227'

2022-01-13 16:33:17: 0: INFO: The job's environment will be merged with the current environment before rendering

2022-01-13 16:33:17: 0: Done executing plugin command of type 'Initialize Plugin'

2022-01-13 16:33:17: 0: Start Job timeout is disabled.

2022-01-13 16:33:17: 0: Task timeout is disabled.

2022-01-13 16:33:17: 0: Loaded job: test2 (61e0b63e4ab1d10d404985b3)

2022-01-13 16:33:17: 0: Successfully mapped R: to \\TC-RENDER1\Projects

2022-01-13 16:33:17: 0: Executing plugin command of type 'Start Job'

2022-01-13 16:33:17: 0: DEBUG: S3BackedCache Client is not installed.

2022-01-13 16:33:17: 0: INFO: Executing global asset transfer preload script 'C:\Users\10923227\AppData\Local\Thinkbox\Deadline10\slave\CS514-021\plugins\61e0b63e4ab1d10d404985b3\GlobalAssetTransferPreLoad.py'

2022-01-13 16:33:17: 0: INFO: Looking for legacy (pre-10.0.26) AWS Portal File Transfer...

2022-01-13 16:33:17: 0: INFO: Looking for legacy (pre-10.0.26) File Transfer controller in C:/Program Files/Thinkbox/S3BackedCache/bin/task.py...

2022-01-13 16:33:17: 0: INFO: Could not find legacy (pre-10.0.26) AWS Portal File Transfer.

2022-01-13 16:33:17: 0: INFO: Legacy (pre-10.0.26) AWS Portal File Transfer is not installed on the system.

2022-01-13 16:33:17: 0: Done executing plugin command of type 'Start Job'

2022-01-13 16:33:17: 0: Plugin rendering frame(s): 1

2022-01-13 16:33:17: 0: Executing plugin command of type 'Render Task'

2022-01-13 16:33:17: 0: INFO: Starting Houdini Job

2022-01-13 16:33:17: 0: INFO: Stdout Redirection Enabled: True

2022-01-13 16:33:17: 0: INFO: Stdout Handling Enabled: True

2022-01-13 16:33:17: 0: INFO: Popup Handling Enabled: True

2022-01-13 16:33:17: 0: INFO: QT Popup Handling Enabled: False

2022-01-13 16:33:17: 0: INFO: WindowsForms10.Window.8.app.* Popup Handling Enabled: False

2022-01-13 16:33:17: 0: INFO: Using Process Tree: True

2022-01-13 16:33:17: 0: INFO: Hiding DOS Window: True

2022-01-13 16:33:17: 0: INFO: Creating New Console: False

2022-01-13 16:33:17: 0: INFO: Running as user: 10923227

2022-01-13 16:33:18: 0: Done executing plugin command of type 'Render Task'

  

=======================================================

Details

=======================================================

Date: 01/13/2022 16:33:20

Frames: 1

Elapsed Time: 00:00:00:06

Job Submit Date: 01/13/2022 16:31:10

Job User: 10596056

Average RAM Usage: 10636726272 (32%)

Peak RAM Usage: 10636726272 (32%)

Average CPU Usage: 6%

Peak CPU Usage: 16%

Used CPU Clocks (x10^6 cycles): 3320

Total CPU Clocks (x10^6 cycles): 55326

  

=======================================================

Worker Information

=======================================================

Worker Name: CS514-021

Version: v10.1.7.1 Release (f5e24d0e2)

Operating System: Windows 10 Enterprise

Running As Service: No

Machine User: 10923227

IP Address: 161.28.108.52

MAC Address: E0:4F:43:29:3D:34

CPU Architecture: x64

CPUs: 8

CPU Usage: 19%

Memory Usage: 9.9 GB / 31.9 GB (31%)

Free Disk Space: 1.091 TB (185.417 GB on C:\, 931.300 GB on D:\)

Video Card: Citrix Indirect Display Adapter
```