%define drakxtools_required_version  12.17
%define drakxtools_conflicted_version  10.4.89

%define libname %mklibname %{name}

Summary:  Tools to configure the keyboard, the mice and the graphic card
Name:     drakx-kbd-mouse-x11
Version:  0.74
Release:  %mkrel 1
Source0:  %name-%version.tar.bz2
License:  GPLv2+
Group:    System/Configuration/Other
Url:      http://www.mandrivalinux.com/en/cvs.php3
BuildRequires: perl-MDK-Common-devel gettext perl-devel
BuildRequires: libxxf86misc-devel ncurses-devel
Requires: drakxtools-curses => %drakxtools_required_version
# need the common pam config files for usermode config
Requires: usermode-consoleonly >= 1.92-4mdv2008.0
%ifnarch %{sunsparc}
Requires: monitor-edid >= 1.12
%endif %{sunsparc}
BuildRoot: %_tmppath/%name-%version-buildroot
# for program:
Conflicts: drakxtools <= %drakxtools_conflicted_version
# for man pages:
Conflicts: drakxtools-curses <= %drakxtools_conflicted_version
# for -noAutoAddDevices:
Conflicts: x11-server-xorg < 1.5.99.3-1.20090110.13
# for Cards+ using nvidia-current|nvidia71xx|nvidia96xx instead of nvidia/nvidia97xx/NVIDIA_LEGACY
Requires: ldetect-lst >= 0.1.174

# we don't want to require X libs (xf86misc is always used inside an eval)
%define _requires_exceptions ^libX

%description
Keyboarddrake enables to configure  the keyboard.
Mousedrake enables to configure the mice.
XFdrake enables to configure the graphic card.

%prep
%setup -q

%build
%make

%install
rm -fr $RPM_BUILD_ROOT
%makeinstall_std

#install lang
%find_lang %name

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

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root)
%doc COPYING NEWS
%config(noreplace) %{_sysconfdir}/pam.d/xfdrake
%config(noreplace) %{_sysconfdir}/security/console.apps/xfdrake
# symlink
%{_sysconfdir}/security/console.apps/XFdrake
%_bindir/XFdrake
%_sbindir/*
%_datadir/libDrakX/pixmaps/*
/usr/lib/libDrakX/auto/*
/usr/lib/libDrakX/xf86misc/main.pm
/usr/lib/libDrakX/Xconfig/*.pm
/usr/lib/libDrakX/*.pm

