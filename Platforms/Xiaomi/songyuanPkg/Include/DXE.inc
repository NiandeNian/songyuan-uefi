  INF MdeModulePkg/Core/Dxe/DxeMain.inf
  INF MdeModulePkg/Universal/PCD/Dxe/Pcd.inf

  INF Binaries/songyuan/EnvDxeEnhanced/EnvDxeEnhanced.inf

  INF MdeModulePkg/Universal/ReportStatusCodeRouter/RuntimeDxe/ReportStatusCodeRouterRuntimeDxe.inf
  INF MdeModulePkg/Universal/StatusCodeHandler/RuntimeDxe/StatusCodeHandlerRuntimeDxe.inf
  INF ArmPkg/Drivers/CpuDxe/CpuDxe.inf
  INF MdeModulePkg/Core/RuntimeDxe/RuntimeDxe.inf
  INF MdeModulePkg/Universal/SecurityStubDxe/SecurityStubDxe.inf

  INF Binaries/songyuan/ShmBridgeDxeLA/ShmBridgeDxeLA.inf
  INF Binaries/songyuan/ScmDxeCompat/ScmDxeCompat.inf
  INF Binaries/songyuan/TzDxeLA/TzDxeLA.inf

  INF MdeModulePkg/Universal/WatchdogTimerDxe/WatchdogTimer.inf
  INF MdeModulePkg/Universal/CapsuleRuntimeDxe/CapsuleRuntimeDxe.inf
  INF MdeModulePkg/Universal/Variable/RuntimeDxe/VariableRuntimeDxe.inf
  INF EmbeddedPkg/EmbeddedMonotonicCounter/EmbeddedMonotonicCounter.inf
  INF MdeModulePkg/Universal/ResetSystemRuntimeDxe/ResetSystemRuntimeDxe.inf
  INF EmbeddedPkg/RealTimeClockRuntimeDxe/RealTimeClockRuntimeDxe.inf
  INF EmbeddedPkg/MetronomeDxe/MetronomeDxe.inf
  INF MdeModulePkg/Universal/HiiDatabaseDxe/HiiDatabaseDxe.inf
  INF ArmPkg/Drivers/ArmGicDxe/ArmGicDxe.inf
  INF ArmPkg/Drivers/TimerDxe/TimerDxe.inf

  INF Binaries/songyuan/ChipInfo/ChipInfo.inf
  INF Binaries/songyuan/IPCCDxe/IPCCDxe.inf
  #INF Binaries/songyuan/GlinkDxe/GlinkDxe.inf
  INF Binaries/songyuan/PlatformInfoDxeDriver/PlatformInfoDxeDriver.inf
  INF Binaries/songyuan/DALSys/DALSys.inf
  INF Binaries/songyuan/HALIOMMU/HALIOMMU.inf
  INF Binaries/songyuan/HWIODxeDriver/HWIODxeDriver.inf
  INF Binaries/songyuan/I2C/I2C.inf
  INF Binaries/songyuan/DALTLMM/DALTLMM.inf
  INF Binaries/songyuan/PmicDxe/PmicDxe.inf

  INF MdeModulePkg/Universal/DevicePathDxe/DevicePathDxe.inf

  INF Binaries/songyuan/DiskIoDxe/DiskIoDxe.inf
  INF Binaries/songyuan/PartitionDxe/PartitionDxe.inf

  INF FatPkg/EnhancedFatDxe/Fat.inf
  INF MdeModulePkg/Universal/Disk/UnicodeCollation/EnglishDxe/EnglishDxe.inf

  INF Binaries/songyuan/UFSDxe/UFSDxe.inf
  INF Binaries/songyuan/CmdDbDxe/CmdDbDxe.inf
  INF Binaries/songyuan/MailboxDxe/MailboxDxe.inf
  INF Binaries/songyuan/QcomScmiDxe/QcomScmiDxe.inf
  INF Binaries/songyuan/Qup/Qup.inf
  INF Binaries/songyuan/I3CMaster/I3CMaster.inf
  INF Binaries/songyuan/PsStateDxe/PsStateDxe.inf
  INF Binaries/songyuan/EXFG/EXFG.inf
  INF Binaries/songyuan/ExLoadSw/ExLoadSw.inf
  INF Binaries/songyuan/PwrUtilsDxe/PwrUtilsDxe.inf
  INF Binaries/songyuan/RpmhDxe/RpmhDxe.inf
  INF Binaries/songyuan/NpaDxe/NpaDxe.inf
  INF Binaries/songyuan/ULogDxe/ULogDxe.inf
  INF Binaries/songyuan/VcsDxe/VcsDxe.inf
  INF Binaries/songyuan/ClockDxe/ClockDxe.inf
  INF Binaries/songyuan/SPMI/SPMI.inf
  INF Binaries/songyuan/ICBDxe/ICBDxe.inf
  INF Binaries/songyuan/SmemDxe/SmemDxe.inf

  INF MdeModulePkg/Universal/BdsDxe/BdsDxe.inf

  INF Binaries/songyuan/RscDxe/RscDxe.inf

  INF EmbeddedPkg/SimpleTextInOutSerial/SimpleTextInOutSerial.inf
  INF MdeModulePkg/Universal/PrintDxe/PrintDxe.inf
  INF MdeModulePkg/Universal/Console/ConPlatformDxe/ConPlatformDxe.inf
  INF MdeModulePkg/Universal/Console/ConSplitterDxe/ConSplitterDxe.inf
  INF MdeModulePkg/Universal/Console/GraphicsConsoleDxe/GraphicsConsoleDxe.inf

!if $(USE_CUSTOM_DISPLAY_DRIVER) == 1
  INF Binaries/songyuan/CPRDxe/CPRDxe.inf
!endif
  INF Binaries/songyuan/GpiDxe/GpiDxe.inf
  INF Binaries/songyuan/SPI/SPI.inf
  INF Binaries/songyuan/SdccDxe/SdccDxe.inf
  INF Binaries/songyuan/FeatureEnablerDxe/FeatureEnablerDxe.inf

!if $(USE_CUSTOM_DISPLAY_DRIVER) == 1
  INF Binaries/songyuan/DisplayDxe/DisplayDxe.inf
!else
  INF SiliciumPkg/Drivers/SimpleFbDxe/SimpleFbDxe.inf
!endif

  INF Binaries/songyuan/ButtonsDxe/ButtonsDxe.inf
  INF Binaries/songyuan/ChargerExDxe/ChargerExDxe.inf
  INF Binaries/songyuan/PmicGlinkDxe/PmicGlinkDxe.inf
  INF Binaries/songyuan/QcomChargerDxeLA/QcomChargerDxeLA.inf
  INF Binaries/songyuan/UsbPwrCtrlDxe/UsbPwrCtrlDxe.inf
  INF Binaries/songyuan/TsensDxe/TsensDxe.inf
  INF Binaries/songyuan/DDRInfoDxe/DDRInfoDxe.inf
  INF Binaries/songyuan/UsbfnDwc3Dxe/UsbfnDwc3Dxe.inf
  INF Binaries/songyuan/XhciPciEmulation/XhciPciEmulation.inf
  INF Binaries/songyuan/XhciDxe/XhciDxe.inf

  INF MdeModulePkg/Bus/Usb/UsbBusDxe/UsbBusDxe.inf
  INF MdeModulePkg/Bus/Usb/UsbKbDxe/UsbKbDxe.inf
  INF MdeModulePkg/Bus/Usb/UsbMassStorageDxe/UsbMassStorageDxe.inf

  INF Binaries/songyuan/UsbMsdDxe/UsbMsdDxe.inf
  INF Binaries/songyuan/UsbDeviceDxe/UsbDeviceDxe.inf
  INF Binaries/songyuan/UsbConfigDxe/UsbConfigDxe.inf
  INF Binaries/songyuan/UsbInitDxe/UsbInitDxe.inf
  INF Binaries/songyuan/UCDxe/UCDxe.inf
  INF Binaries/songyuan/RngDxe/RngDxe.inf
  INF Binaries/songyuan/PILDxe/PILDxe.inf
  INF Binaries/songyuan/PILProxyDxe/PILProxyDxe.inf
  INF Binaries/songyuan/SPSSDxe/SPSSDxe.inf
