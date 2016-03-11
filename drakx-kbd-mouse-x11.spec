%define	_libexecdir %{_prefix}/libexec
%define libname lib%{name}

Summary:	Tools to configure the keyboard, the mice and the graphic card
Name:		drakx-kbd-mouse-x11
Version:	1.2.2
Release:	3
License:	GPLv2+
Group:		System/Configuration/Other
Url:		https://abf.rosalinux.ru/moondrake/drakx-kbd-mouse-x11
Source0:	%{name}-%{version}.tar.xz
BuildRequires:	gettext
BuildRequires:	perl-MDK-Common-devel
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(xxf86misc)
BuildRequires:	intltool
Requires:	drakxtools-curses
Requires:	%{libname} = %{EVRD}
Requires:	ldetect-lst >= 0.1.327.6
Requires:	perl-LDetect >= 0.13.11-2
Requires:	polkit
Requires:	xdm
%ifnarch %{sparcx} %{arm} %{mips}
Requires:	monitor-edid >= 1.12
%endif
Conflicts:	drakxtools-curses < 14.56-6
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

%package -n	%{libname}
Summary:	DrakX X11 tools library
Group:		System/Configuration/Other
Conflicts:	drakx-kbd-mouse-x11 < 0.113

%description -n %{libname}
This package contains the DrakX X11 tools library.

%prep
%setup -q

%build
%make OPTIMIZE="%{optflags}"

%install
%makeinstall_std

%find_lang %{name}

# add nokmsboot if necessary and rebuild initrds so that they handle it
%triggerpostun -- drakx-kbd-mouse-x11 < 0.91
perl -I%{_prefix}/lib/libDrakX -MXconfig::various -e 'Xconfig::various::setup_kms();' &>/dev/null
%{_sbindir}/bootloader-config --action rebuild-initrds || :

%files -f %{name}.lang
%doc COPYING NEWS
/sbin/display_driver_helper
%{_sbindir}/drakx-update-background
%{_bindir}/drakkeyboard
%{_bindir}/drakmouse
%{_bindir}/drakx11
%{_bindir}/keyboarddrake
%{_bindir}/mousedrake
%{_bindir}/XFdrake
%{_bindir}/Xdrakres
%{_libexecdir}/drakkeyboard
%{_libexecdir}/drakmouse
%{_libexecdir}/drakx11
%{_datadir}/polkit-1/actions/*.policy

%files -n %{libname}
%{_datadir}/libDrakX/pixmaps/*
%{_prefix}/lib/libDrakX/auto/*
%{_prefix}/lib/libDrakX/xf86misc/main.pm
%{_prefix}/lib/libDrakX/Xconfig/*.pm
%dir %{_prefix}/lib/libDrakX/Xconfig
%{_prefix}/lib/libDrakX/*.pm
