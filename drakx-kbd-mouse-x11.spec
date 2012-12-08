%define drakxtools_required_version  12.40
%define drakxtools_conflicted_version  10.4.89

Summary: 	Tools to configure the keyboard, the mice and the graphic card
Name:		drakx-kbd-mouse-x11
Version:	0.97
Release:	1
Source0:	%{name}-%{version}.tar.xz
License:	GPLv2+
Group:		System/Configuration/Other
Url:		https://abf.rosalinux.ru/soft/drakx-kbd-mouse-x11
BuildRequires:	perl-MDK-Common-devel gettext perl-devel
BuildRequires:	libxxf86misc-devel ncurses-devel
Requires:	drakxtools-curses => %drakxtools_required_version
# need the common pam config files for usermode config
Requires:	usermode-consoleonly >= 1.92-4mdv2008.0
%ifnarch %{sparcx} %{arm} %{mips}
Requires:	monitor-edid >= 1.12
%endif
# for program:
Conflicts:	drakxtools <= %drakxtools_conflicted_version
# for man pages:
Conflicts:	drakxtools-curses <= %drakxtools_conflicted_version
# for -noAutoAddDevices:
Conflicts:	x11-server-xorg < 1.5.99.3-1.20090110.13
# for Cards+ using nvidia-current|nvidia71xx|nvidia96xx instead of nvidia/nvidia97xx/NVIDIA_LEGACY
Requires:	ldetect-lst >= 0.1.312
# for nokmsboot (initrds have to have nokmsboot support and udev has to handle it)
Conflicts:	mkinitrd < 6.0.93-22
Conflicts:	dracut < 008-6
Conflicts:	udev < 165-5

# we don't want to require X libs (xf86misc is always used inside an eval)
%define  __noautoreq ^libX

%description
Keyboarddrake enables to configure  the keyboard.
Mousedrake enables to configure the mice.
XFdrake enables to configure the graphic card.

%prep
%setup -q

%build
%make OPTIMIZE="%{optflags} -Os"

%install
%makeinstall_std

#install lang
%find_lang %{name}

# consolehelper configuration
# ask for user password
ln -s %{_bindir}/consolehelper %{buildroot}%{_bindir}/XFdrake
mkdir -p %{buildroot}%{_sysconfdir}/pam.d/
ln -sf %{_sysconfdir}/pam.d/mandriva-simple-auth %{buildroot}%{_sysconfdir}/pam.d/xfdrake
mkdir -p %{buildroot}%{_sysconfdir}/security/console.apps
cat > %{buildroot}%{_sysconfdir}/security/console.apps/xfdrake <<EOF
USER=<user>
PROGRAM=/usr/sbin/XFdrake
FALLBACK=false
SESSION=true
EOF

ln -s %{_sysconfdir}/security/console.apps/xfdrake \
        %{buildroot}%{_sysconfdir}/security/console.apps/XFdrake

# add nokmsboot if necessary and rebuild initrds so that they handle it
%triggerpostun -- drakx-kbd-mouse-x11 < 0.91
perl -I/usr/lib/libDrakX -MXconfig::various -e 'Xconfig::various::setup_kms();' &>/dev/null
%{_sbindir}/bootloader-config --action rebuild-initrds || :

%files -f %{name}.lang
%doc COPYING NEWS
%config(noreplace) %{_sysconfdir}/pam.d/xfdrake
%config(noreplace) %{_sysconfdir}/security/console.apps/xfdrake
# symlink
%{_sysconfdir}/security/console.apps/XFdrake
/sbin/display_driver_helper
%_bindir/XFdrake
%_sbindir/*
%_datadir/libDrakX/pixmaps/*
/usr/lib/libDrakX/auto/*
/usr/lib/libDrakX/xf86misc/main.pm
/usr/lib/libDrakX/Xconfig/*.pm
%dir /usr/lib/libDrakX/Xconfig
/usr/lib/libDrakX/*.pm


%changelog
* Thu Nov 27 2012 akdengi <akdengi> 0.97-1
- 0.97
- Change Quit to Apply settings. Really delete xorg.conf for non-proprietary drivers
- Skip test. Not write Xorg.conf, only for proprietary blobs
- Not need detect XAA/EXA - all card since XServer 13 use EXA only
- Use Plug'n'play as default to all. Not need detect oldest devices
- Install kernel-devel-latest if not present in system for current kernel (by uname -r)

* Fri Nov 16 2012 akdengi <akdengi> 0.95-1
- fix update-alternatives error with blob install

* Fri Aug 17 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.93-1
+ Revision: 815166
- load evdev slightly earlier and in actual time before required
- compile with %%{optflags}
- new version:
  o do not install bootloader when configuring X during install.
    this will be done at end of summary to allow selecting where
    to install bootloader (mga#5044)
  o fix crash regression (mga#5238)
  o display_driver_helper:
    - drop support for unused and unuseful --check-initrd option
    - allow use of nouveau without xorg.conf as it is now autoselected by
      X server in that case
    - load radeon module with modeset=0 when no firmware is installed
      (see mga#3466)
    - report KMS as not allowed with --is-kms-allowed on radeon hardware
      without radeon firmware, so that 'nokmsboot' will be used on such
      cases
    - add --setup-boot-kms action which sets/unsets 'nokmsboot' boot
      option as necessary
  o do not generate a xorg.conf symlink pointing to nothing if
    xorg.conf.standard exists
  o do not run setxkbmap during text install
  o handle drivers needing firmware (mga#1471, mga#3421, mga#3466)
  o handle drivers needing SSE
  o convert mouse helper to use udevadm in order to work with udev 175+
  o default to 24bit with QXL driver (16 bit doesn't work)
  o do not offer to try KMS drivers during installation (mga#3711)
  o display_driver_helper: use the new modprobe --resolve-alias instead
    if manually parsing --dry-run output
  o fix path to 'loadkeys'
  o runlevel: Ensure that systemd targets corresponding to the required
    runlevel are also updated (in addition to inittab).
  o fallback to X server run-time autodetection on laptops instead of
    1024x768 when the monitor could not be probed (Mageia #1059)
  o do not try to probe monitor information via X server on laptops (it
    doesn't work with recent X servers)
  o add support for Asturian keyboard
  o prefer boot display devices when probing cards (fixes at least an issue
    with an SLI laptop as reported by Maarten Vanraes)
  o harddrake: configure default resolution (and background) even if card
    configuration fails (useful if vbox video driver is not available)
  o evdev needs to be loaded before calling getInputDevices_and_usb
    else it will lead to a crash (pterjan)
  o display_driver_helper: do not load radeon driver if the proprietary
    driver is temporarily disabled on a PowerXpress system
  o display_driver_helper: allow automatic loading of the implicit driver
    on systems without xorg.conf if the presence of other files indicates
    that this is not a live cd boot before automatic X.org configuration
    (fixes radeon KMS without xorg.conf)
- fix external-depfilter-with-internal-depgen
- cleanups

* Fri Jan 27 2012 Paulo Andrade <pcpa@mandriva.com.br> 0.92-4
+ Revision: 769235
- Rebuild with newer perl.

* Mon Aug 08 2011 Alex Burmashev <burmashev@mandriva.org> 0.92-3
+ Revision: 693646
- changed tmp dir from home to TMPDIR env

  + Matthew Dawkins <mattydaw@mandriva.org>
    - disable monitor-edid on arm/mips

* Wed Jun 29 2011 Alex Burmashev <burmashev@mandriva.org> 0.92-2
+ Revision: 688267
- changed ru(winkeys) to ru

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - rename %%{sunspace} to %%{sparcx}

* Thu Apr 21 2011 Anssi Hannula <anssi@mandriva.org> 0.92-1
+ Revision: 656362
- version 0.92
  o disable debug output of display_driver_helper by default
  o fix ahead-of-X-server loading of proprietary and fglrx kernel modules
  o try unloading unconfigured drivers in "display_driver_helper
    --check-loaded"

* Sun Apr 17 2011 Anssi Hannula <anssi@mandriva.org> 0.91-1
+ Revision: 654050
- version 0.91
  o use UseEdid instead of IgnoreEDID with nvidia96xx since the latter is
    obsolete (#40006)
  o remove "3D hardware acceleration" from the UI, it will always be enabled
    by default since we unconditionnally add the "dri" module to xorg.conf now
    (#58933)
  o add display_driver_helper script (used by XFdrake, udev, drakx, dkms)
  o add/remove nokmsboot boot option as needed
  o ask for reboot instead of X server restart, as it is commonly needed

* Thu Dec 02 2010 Oden Eriksson <oeriksson@mandriva.com> 0.90-2mdv2011.0
+ Revision: 604828
- rebuild

* Wed May 26 2010 Christophe Fergeau <cfergeau@mandriva.com> 0.90-1mdv2010.1
+ Revision: 546208
- 0.90
- translation updates

* Tue May 11 2010 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 0.89-1mdv2010.1
+ Revision: 544494
- 0.89:
  - mouse:
    o remove imwheel support

* Thu Feb 25 2010 Christophe Fergeau <cfergeau@mandriva.com> 0.88-1mdv2010.1
+ Revision: 511109
- 0.88:
- rename wacom driver package to its current name
- remove obsoleted video drivers from video driver list, add some new ones

* Tue Feb 09 2010 Anssi Hannula <anssi@mandriva.org> 0.87-1mdv2010.1
+ Revision: 503367
- 0.87
- XFdrake:
  o use -X option for ldconfig when switching alternatives, we only need the
    cache rebuilt
  o do not disable Composite extension by default when using fglrx driver
  o do not disable loading of dri module for non-glx drivers, as KMS drivers
    require it as well
  o do not disable loading of glx module for fbdev, in order to allow AIGLX
    to work in software rasterizer mode
  o do not add dbe and extmod modules to xorg.conf anymore, they are loaded
    by default anyway

* Fri Nov 27 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.86-1mdv2010.1
+ Revision: 470470
- keyboarddrake:
    o make sure to properly init the console keymap before dumping it during
      initial configuration, should fix console keymap setting in finish-install

* Thu Oct 22 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.85-2mdv2010.0
+ Revision: 458923
- 0.85:
- mousedrake:
    o fix input module path on 64 bit machines
    o don't install input drivers if X isn't here
- XFdrake:
    o enable ctrl+alt+backspace by default

* Wed Oct 21 2009 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 0.84-2mdv2010.0
+ Revision: 458546
- Enable ctrl+alt+backspace by default

* Fri Oct 09 2009 Olivier Blin <blino@mandriva.org> 0.84-1mdv2010.0
+ Revision: 456365
- 0.84
- run ldconfig after update-alternatives during installer too
  (psb alternative does not have a higher priority than standard
   alternative, and ldconfig was run by the installer only before
   manually setting the alternative, which was not enough)

* Thu Oct 08 2009 Olivier Blin <blino@mandriva.org> 0.83-1mdv2010.0
+ Revision: 456142
- 0.83
- use 28.8kHz as lower HorizSync (for 800x480)

* Wed Sep 23 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.82-1mdv2010.0
+ Revision: 447822
- 0.82:
- don't consider xorg.conf files with no InputDevice sections as invalid, fixes   bug reported on cooker mailing list

* Wed Sep 23 2009 Olivier Blin <blino@mandriva.org> 0.81-1mdv2010.0
+ Revision: 447794
- 0.81
- add psb driver support (for Poulsbo chipset)

* Tue Sep 22 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.80-1mdv2010.0
+ Revision: 447352
- 0.80:
- XFdrake:
  o don't write sections in xorg.conf for USB wacom tablets, Synaptics
    touchpads, mouses using "evdev" or "mouse" and keyboards

* Mon Sep 14 2009 Olivier Blin <blino@mandriva.org> 0.79-1mdv2010.0
+ Revision: 440578
- 0.79
- XFdrake:
  o fix DontZap option issue with old xorg.conf files
- allow to skip framebuffer setup (and thus splash removal)
  for newer harddrake releases

* Fri Sep 11 2009 Aurélien Lefebvre <alefebvre@mandriva.com> 0.78-2mdv2010.0
+ Revision: 438498
- XFdrake:
  o fix DontZap option issue with old xorg.conf file

* Wed Sep 09 2009 Aurélien Lefebvre <alefebvre@mandriva.com> 0.78-1mdv2010.0
+ Revision: 435706
- XFdrake:
  o added "Disable Ctrl-Alt-Backspace" option

* Wed Jul 22 2009 Anssi Hannula <anssi@mandriva.org> 0.77-1mdv2010.0
+ Revision: 398517
- XFdrake:
  o correctly detect proprietary drivers that are located in
    /usr/lib/drivername/xorg (#52384)
  o when probing for video cards, ignore cards which are not in the VIDEO_VGA
    PCI class (it is pretty common for dual-head ATI cards to have a
    VIDEO_OTHER device for example). This has the potential of breaking
    dual head setups, so it needs careful testing in Cooker ;) See bug #48028
  o fix crash when both monitor and driver can not be probed (in
    harddrake service or XFdrake --auto), for example with some Quanta
    IL1 netbooks using Chrome9 IC3
- keyboarddrake:
  o update the xkb HAL keys when the keyboard layout is changed so that it
    persists after a X server restart. Bug #49725

  + Christophe Fergeau <cfergeau@mandriva.com>
    - Raise required version of drakx

  + Thierry Vignaud <tv@mandriva.org>
    - own /usr/lib/libDrakX/Xconfig

* Wed Apr 22 2009 Thierry Vignaud <tv@mandriva.org> 0.74-1mdv2009.1
+ Revision: 368669
- mousedrake:
  o fix vmmouse configuration for vmware (#49654)

* Tue Apr 21 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.73-1mdv2009.1
+ Revision: 368523
- 0.73:
- tweak Intel driver accel methods in xorg.conf so that it's more consistent
  with what the new Intel driver expects.

* Wed Apr 15 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.72-1mdv2009.1
+ Revision: 367370
- Update tarball for 0.72 release
- 0.72:
- XFdrake:
  o fix selecting proprietary drivers with xdriver=DRIVER boot option
  o do not add Load "freetype" to xorg.conf as the module does not exist
    anymore
  o use Plug'n'Play monitor when in vbox and don't specify any default
    resolution, fixes #49642

* Thu Apr 02 2009 Anssi Hannula <anssi@mandriva.org> 0.71-1mdv2009.1
+ Revision: 363558
- 0.71
- XFdrake:
  o add support for xdriver=DRIVER kernel boot option that affects
    non-interactive device autodetection, e.g. One boot
    (special value xdriver=free disables proprietary drivers)
  o add nouveau driver into the driver list

* Fri Mar 20 2009 Anssi Hannula <anssi@mandriva.org> 0.70-1mdv2009.1
+ Revision: 359185
- 0.70
- mousedrake:
  o configure input driver as 'vmmouse' if running in vmware (#29106)
  o test if the file is there before trying to install the packages, that saves
    a rpm -q in harddrake service after adding/removing/changing a mouse
- XFdrake:
  o adapt for recent changes in proprietary driver alternatives

  + Thierry Vignaud <tv@mandriva.org>
    - bump require on drakxtools for the vmmouse fix

* Thu Jan 29 2009 Pixel <pixel@mandriva.com> 0.69-1mdv2009.1
+ Revision: 335308
- XFdrake:
  o use option -noAutoAddDevices when testing X
    (useful during installation, #47237)
- conflicts with x11-server-xorg which do not handle -noAutoAddDevices

* Wed Jan 28 2009 Pixel <pixel@mandriva.com> 0.68-1mdv2009.1
+ Revision: 334889
- 0.68
- keyboarddrake:
  o bug fix: overwrite previous /etc/sysconfig/keyboard Xkb information when
    changing keyboard

* Thu Jan 08 2009 Pixel <pixel@mandriva.com> 0.67-1mdv2009.1
+ Revision: 327080
- 0.67:
- mousedrake:
  o synaptics driver in now in package x11-driver-input-synaptics (#45531)

* Thu Dec 18 2008 Pixel <pixel@mandriva.com> 0.66-1mdv2009.1
+ Revision: 315643
- 0.66:
- keyboarddrake:
  o do not configure hal directly, but write in /etc/sysconfig/keyboard Xkb
    information so hal can get them
  o new option "--migrate" which adds Xkb information in
    /etc/sysconfig/keyboard
  o correctly handle default XkbModel
    (so that we do not force pc105 when we should not)

* Mon Dec 08 2008 Pixel <pixel@mandriva.com> 0.65-1mdv2009.1
+ Revision: 311770
- 0.65:
- keyboarddrake:
  o configure hal so Xorg can get xkb info
    (nb: for now, you must "service haldaemon restart" to be taken into account)
- XFdrake:
  o generic flat planel must allow "800x480 @ 60.00 Hz (GTF) hsync: 29.82 kHz"
    so "HorizSync 31.5-90" is too strict, generating "HorizSync 29.5-90"
  o have Option "PanelGeometry" "XXxYY" on geode driver
  o do not display the weird ratios 128/75, 85/48 (for 1024x600 and 1360x768)
  o do not load "Type1" module by default (disabled in xserver-1.5.x)
  o special hack for gdium: the "default monitor" is "Plug'n Play" instead of
    good_default_monitor() (it will work since the resolution is passed to the
    kernel on gdium)
  o there is no reason "automatic" resolution should imply "automatic" color
    depth
- mousedrake, XFdrake:
  o do not use /dev/mouse symlink (in xorg.conf)
- mousedrake
  o do not propose to test the chosen mice
    (it doesn't handle evdev/synaptics and so is quite obsolete nowadays)

* Wed Oct 08 2008 Pixel <pixel@mandriva.com> 0.64-2mdv2009.1
+ Revision: 291224
- transform a conflict into a require to help rpmlib on mdv2007.1 upgrade

* Wed Oct 01 2008 Pixel <pixel@mandriva.com> 0.64-1mdv2009.0
+ Revision: 290356
- 0.64:
- XFdrake:
  o explicitly Load or Disable module "dri"
    (to be independent of Xorg's default choice)

* Tue Sep 30 2008 Thierry Vignaud <tv@mandriva.org> 0.63-1mdv2009.0
+ Revision: 289964
- updated translation

* Thu Sep 25 2008 Pixel <pixel@mandriva.com> 0.62-1mdv2009.0
+ Revision: 288154
- 0.62:
- XFdrake:
  o set "PreferredMode" in Monitor section if the user changes the resolution
   (we still do not use PreferredMode for the default resolution)

* Thu Sep 11 2008 Pixel <pixel@mandriva.com> 0.61-1mdv2009.0
+ Revision: 283822
- 0.61:
- keyboarddrake:
  o fix lithuanian keyboard choices (cf #41031)
- XFdrake:
  o do set a background image when using resolution "Automatic" (#43644)

* Tue Sep 09 2008 Pixel <pixel@mandriva.com> 0.60-1mdv2009.0
+ Revision: 283135
- 0.60:
- XFdrake:
  o allow xorg.conf to have no "Monitor" section (#42793)
  o [bugfix] fix clicking on "Options" when Composite is disabled
    (regression introduced in 0.58) (#43710)

* Mon Aug 18 2008 Pixel <pixel@mandriva.com> 0.59-1mdv2009.0
+ Revision: 273192
- 0.59:
- XFdrake:
  o use 24dpp by default, even on DRI (needed for kde4)
  o ensure we don't drop non-main "Device" (when modifying "Options", #41410)
  o use nvidia-current default settings for nvidia173 as well
  o no need to force XaaNoOffscreenPixmaps, it is the default now in
    x11-server

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 0.58-2mdv2009.0
+ Revision: 220705
- rebuild

  + Pixel <pixel@mandriva.com>
    - 0.58:
    - XFdrake:
      o Composite is now the default in xserver 1.4 (#35043)
      o do not create symlink /etc/X11/X to ../../usr/bin/Xorg (#41363)
      o drop support for /etc/X11/XF86Config (replaced by xorg.conf for some time now)
    - mousedrake:
      o evdev and imwheel handle orthogonal things, so do use imwheel even if we
      need evdev (#40088)

* Wed Apr 02 2008 Pixel <pixel@mandriva.com> 0.57-1mdv2008.1
+ Revision: 191648
- 0.57:
- XFdrake:
  o workaround pb with nvidia driver: make dm restart xserver (#38297)

* Wed Apr 02 2008 Pixel <pixel@mandriva.com> 0.56-1mdv2008.1
+ Revision: 191640
- 0.56:
- XFdrake:
  o do not disable RenderAccel on nvidia-current
    (regression introduced in 0.21)

* Thu Mar 27 2008 Pixel <pixel@mandriva.com> 0.55-1mdv2008.1
+ Revision: 190640
- 0.55:
- XFdrake:
  o disable "DynamicTwinView" when not using TwinView (#39171)

* Tue Mar 25 2008 Pixel <pixel@mandriva.com> 0.54-1mdv2008.1
+ Revision: 189931
- 0.54
- keyboarddrake library:
  o in drakx-finish-install, keyboard is asked after asking country, so have a
    good default based on country too (was done for pt_BR but not fr_XX)
    (#39221)

* Fri Mar 21 2008 Pixel <pixel@mandriva.com> 0.53-1mdv2008.1
+ Revision: 189379
- 0.53:
- XFdrake:
  o allow to set "EXA" on "intel" driver (#39162)

* Thu Mar 20 2008 Pixel <pixel@mandriva.com> 0.52-1mdv2008.1
+ Revision: 189168
- 0.52:
- XFdrake:
  o add option "Force display mode of DVI" on driver "nvidia" (#30066)
- XFdrake library:
  o ensure set_default_background() doesn't fail (#39065)
    (ie default to 1024x768 if 0x0 is given)

* Wed Mar 19 2008 Pixel <pixel@mandriva.com> 0.51-1mdv2008.1
+ Revision: 188829
- 0.51:
- XFdrake:
  o use 24bpp on savage (#38750)
  o do use EDID HorizSync/VertRefresh on 16/10 (regression introduced in 0.50)
- keyboarddrake:
  o default romanian keyboard is qwerty (cf #38450)
  o "ro" really is "ro(std_cedilla)"
    (to be more standard on unpatched xkeyboard-config)
  o "ro(us)" is wrong and not qwerty, use "ro(winkeys)" which is the only
    qwertz from symbols/ro

* Tue Mar 11 2008 Pixel <pixel@mandriva.com> 0.50-1mdv2008.1
+ Revision: 185860
- 0.50:
- XFdrake:
  o if the EDID gives a valid 16/10 preferred resolution (even if duplicated),
    but no HorizSync/VertRefresh, use a generic flat panel
    HorizSync/VertRefresh (needed for edid.lcd.dell-inspiron-6400, #37971)
  o handle DRIVER2_NO_SSE (from Cards+), needed by nvidia-current requiring SSE

* Thu Feb 28 2008 Pixel <pixel@mandriva.com> 0.49-1mdv2008.1
+ Revision: 176384
- 0.49:
- XFdrake: background images are now jpeg files

* Thu Feb 28 2008 Pixel <pixel@mandriva.com> 0.48-1mdv2008.1
+ Revision: 176049
- 0.48:
- XFdrake:
  o when setting background for the resolution, handle "hour"-based
    backgrounds (also add Mandriva.xml symlink)

* Wed Feb 27 2008 Pixel <pixel@mandriva.com> 0.47-1mdv2008.1
+ Revision: 175772
- 0.47:
- XFdrake:
  o when setting background for the resolution, handle "hour"-based backgrounds

* Mon Feb 18 2008 Pixel <pixel@mandriva.com> 0.46-1mdv2008.1
+ Revision: 171486
- 0.46:
- XFdrake:
  o add 1024x600 (used on Samsung Q1Ultra) (#37889)

* Tue Feb 05 2008 Pixel <pixel@mandriva.com> 0.45-1mdv2008.1
+ Revision: 162578
- 0.45:
- XFdrake:
  o add 800x480 (used on belinea s.book) (#37486)

* Fri Jan 25 2008 Pixel <pixel@mandriva.com> 0.44-1mdv2008.1
+ Revision: 157893
- 0.44:
- library for installer:
  o do not force "us" keyboard on everybody that choose "English (American)"
    (#36575)

* Wed Jan 23 2008 Pixel <pixel@mandriva.com> 0.43-1mdv2008.1
+ Revision: 157017
- 0.43
- XFdrake:
  o if the EDID gives a valid EISA_ID, a valid 16/10 preferred resolution, but
    no HorizSync/VertRefresh, use a generic flat panel HorizSync/VertRefresh

* Tue Jan 22 2008 Pixel <pixel@mandriva.com> 0.42-1mdv2008.1
+ Revision: 156427
- 0.42:
- XFdrake:
  o sort monitors in text mode so that "Generic|..." monitors do not appear
    in the middle of "Vendor|..." monitors
- use SendCoreEvents instead of AlwaysCore for wacoms
- mousedrake:
  o use udev in $PATH instead of /lib/udev/usb_id
    (need latest udev pkg)

* Tue Jan 15 2008 Thierry Vignaud <tv@mandriva.org> 0.41-2mdv2008.1
+ Revision: 152146
- rebuild
- kill re-definition of %%buildroot on Pixel's request

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Fri Dec 14 2007 Olivier Blin <blino@mandriva.org> 0.41-1mdv2008.1
+ Revision: 120129
- 0.41
- mousedrake:
  o use SendCoreEvents instead of AlwaysCore for Synaptics touchpads (#36140)

* Mon Dec 10 2007 Pixel <pixel@mandriva.com> 0.40-1mdv2008.1
+ Revision: 116878
- 0.40:
- XFdrake:
  o never write a ModeLine when using fglrx driver (#30934)

* Fri Nov 30 2007 Pixel <pixel@mandriva.com> 0.39-1mdv2008.1
+ Revision: 114098
- 0.39:
- keyboarddrake:
  o use kr(kr104) for the korean keyboard, and don't prompt for a toggle key
    since korean use input method instead
- use /dev/input/by-id/xxx device instead of vendor+product for evdev mice
  (vendor+product support is dropped in x11-driver-input-evdev-1.2.0)
- fix device /dev/input/by-id/usb-$ID_SERIAL-event-mouse for wacoms
  when the ID_SERIAL contains special chars

* Thu Nov 01 2007 Anssi Hannula <anssi@mandriva.org> 0.38-1mdv2008.1
+ Revision: 104691
- 0.38
  o display message "This setting will be activated after the
    installation." only during installation (Pixel)
  o handle new fglrx packages with fglrx_dri.so handled by alternatives

* Thu Oct 04 2007 Pixel <pixel@mandriva.com> 0.37-1mdv2008.0
+ Revision: 95467
- 0.37:
- if we probe a monitor EISA_ID but we don't have corresponding
  HorizSync/VertRefresh, we must not the monitor info
- when checking dkms module packages, check that modules are either
  available in urpmi media, or already installed (fix detection in live)

* Thu Oct 04 2007 Pixel <pixel@mandriva.com> 0.36-1mdv2008.0
+ Revision: 95308
- 0.36:
- better fix for typo in 0.32: don't wrongly default to "automatic" resolution
  when creating xorg.conf (in non --auto) (#34453)

* Wed Oct 03 2007 Thierry Vignaud <tv@mandriva.org> 0.35-1mdv2008.0
+ Revision: 95066
- updated translation

* Mon Oct 01 2007 Thierry Vignaud <tv@mandriva.org> 0.34-1mdv2008.0
+ Revision: 94300
- updated translation

* Fri Sep 28 2007 Olivier Blin <blino@mandriva.org> 0.33-1mdv2008.0
+ Revision: 93772
- require drakxtools >= 10.4.221 for VirtualBox detection
- 0.33
- we don't set ModulesPath to DRI_GLX_SPECIAL value, so we must read it
  differently so that Xconfig::various::info() is correct (#31326)
- add support for x11-driver-input-vboxmouse when inside a VirtualBox guest
- fix typo in 0.32: don't wrongly default to "automatic" resolution when
  creating xorg.conf (in non --auto)

* Wed Sep 26 2007 Pixel <pixel@mandriva.com> 0.32-1mdv2008.0
+ Revision: 93050
- 0.32:
- monitor-probe-using-X can now return EDIDs. if Xorg find an EDID (whereas
  monitor-get-edid-using-vbe failed), defaults to "Plug'n Play" monitor (ie
  let Xorg do things automatically) instead of good_default_monitor.
  (requires monitor-edid 1.12)
- fix typo in 0.30: do not use "Automatic" resolution by default in --auto

* Tue Sep 25 2007 Thierry Vignaud <tv@mandriva.org> 0.31-1mdv2008.0
+ Revision: 92925
- updated translations

* Tue Sep 25 2007 Pixel <pixel@mandriva.com> 0.30-1mdv2008.0
+ Revision: 92836
- 0.30:
- add support for "Automatic" resolution (aka "let xorg do everything")
- when user asks for "Plug'n Play", silently default to Xorg auto-detection
  when we fail to auto-detect

* Fri Sep 21 2007 Olivier Blin <blino@mandriva.org> 0.29-1mdv2008.0
+ Revision: 91806
- 0.29
- unload drivers loaded by monitor-probe-using-X
  (fix fglrx usage when harddrake probes using X and loads radeon driver)

* Thu Sep 20 2007 Pixel <pixel@mandriva.com> 0.28-1mdv2008.0
+ Revision: 91561
- 0.28:
- when using evdev for mice, ensure it doesn't match a keyboard
  (eg: in case of a mouse+keyboard combo) (#32905)
- fix regression in 0.24: remove bogus duplicates in monitors tree (#33778)

* Wed Sep 19 2007 Pixel <pixel@mandriva.com> 0.27-1mdv2008.0
+ Revision: 91012
- 0.27:
- for evdev configured mice, specify bustype
  (useful for "Macintosh mouse button emulation" which has same vendor/product
   as "AT Translated Set 2 keyboard")
  (need drakxtools-backend 10.4.203)

* Mon Sep 17 2007 Pixel <pixel@mandriva.com> 0.26-1mdv2008.0
+ Revision: 89159
- 0.26: handle fglrx-hd2000 driver (Anssi)

* Wed Sep 12 2007 Andreas Hasenack <andreas@mandriva.com> 0.25-2mdv2008.0
+ Revision: 84827
- use new common pam config files for usermode/consolehelper

* Mon Sep 10 2007 Pixel <pixel@mandriva.com> 0.25-1mdv2008.0
+ Revision: 84000
- 0.25:
- in the list of available Xorg drivers, add "Driver" from Cards+
  (will ease the maintainance of the list of drivers in Xconfig/card.pm)
- minimal support for allowing to choose evdev on all mice

* Fri Sep 07 2007 Pixel <pixel@mandriva.com> 0.24-1mdv2008.0
+ Revision: 81477
- 0.24:
- do not configure XFS, it's useless
- fix default_headers (ie allow XFdrake to create xorg.conf from scratch again)
- keep the order from MonitorsDB file
  (allows "Flat Panel 800x600" to be before "Flat Panel 1024x768")
  (needs a nicely sorted MonitorsDB though)
- correct license (GPLv2+)

* Thu Sep 06 2007 Pixel <pixel@mandriva.com> 0.23-1mdv2008.0
+ Revision: 80593
- 0.23: do not start xfs for the test (#33219)

* Wed Aug 29 2007 Andreas Hasenack <andreas@mandriva.com> 0.22-2mdv2008.0
+ Revision: 74705
- allow XFdrake to be run as root by console user with password

* Mon Aug 27 2007 Pixel <pixel@mandriva.com> 0.22-1mdv2008.0
+ Revision: 71952
- new release, 0.22
- do configure XFS if installed
- when removing/replacing an InputDevice section, ensure we remove the
  corresponding entry in ServerLayout. ie do not rely on InputDevice sections
  to use XFdrake-compatible Identifiers (as suggested by fcrozat)
- add avivo in the Xorg drivers list
- handle libglx.so provided by standard.conf alternative
- handle x11-driver-video-fglrx instead of ati

* Wed Aug 08 2007 Pixel <pixel@mandriva.com> 0.21-1mdv2008.0
+ Revision: 60556
- new release, 0.21 (conflicts with ldetect-lst < 0.1.174)
- handle nvidia-current instead of nvidia97xx (thanks to Anssi)
- handle x11-driver-video-$nvidia instead of $nvidia
- adapt to kbd instead of console-tools: s/kmap/map/

* Fri Aug 03 2007 Pixel <pixel@mandriva.com> 0.20-1mdv2008.0
+ Revision: 58638
- new release, 0.20
- fix detection of touchpad on some kernels (#31584)
  (need drakxtools-backend >= 10.4.145)
- internal: add many options as having to be used only once, easing their use
  and fixing setting them
  (eg #31942 where one can't click "Options" after setting EXA)
- drop support for installing/configuring 915resolution
  (no more needed since x11-driver-video-intel 2.0)
- do not configure using xfs anymore (#32051)

* Mon Jul 09 2007 Pixel <pixel@mandriva.com> 0.19-1mdv2008.0
+ Revision: 50624
- new release, 0.19
- wacom configuration:
  o enhance configuration by using /dev/input/by-id/xxx
    (need drakxtools-backend >= 10.4.144)
  o add "pad" InputDevice section
- fix displaying "3D hardware acceleration: no" for nvidia proprietary driver
  (#31326)

* Thu Jun 14 2007 Pixel <pixel@mandriva.com> 0.18-1mdv2008.0
+ Revision: 39296
- new release, 0.18
- handle resolution switch via xrandr without restarting X (#30896)
- add 1366x768, 1360x768 and 1360x765 resolutions
- add big standard resolutions (4/3, 16/10, 16/9)
- [bugfix] fix test message not translated (#30261)
- remove all fglrx options, hopefully default is good enough
  (and at least MonitorLayout option is depreacated as reported on cooker)

* Tue May 15 2007 Thierry Vignaud <tv@mandriva.org> 0.17-2mdv2008.0
+ Revision: 26963
- package NEWS instead of ChangeLog

* Wed May 09 2007 Pixel <pixel@mandriva.com> 0.17-1mdv2008.0
+ Revision: 25426
- new release, 0.17
- fix using proprietary driver (remove debug code) (thanks to Michael Altizer)

* Mon Apr 30 2007 Pixel <pixel@mandriva.com> 0.16-1mdv2008.0
+ Revision: 19528
- new release, 0.16
- ask "Do you wish to use proprietary driver" before installing the needed packages
- don't use 1280x1024 prefered resolution
  (using prefered resolution only when adding explicit gtf modelines)
- handle new intel driver (including migration from "i810")
- workaround buggy fglrx driver: make dm restart xserver (#29550)

