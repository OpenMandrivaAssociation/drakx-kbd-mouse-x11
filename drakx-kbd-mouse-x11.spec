%define drakxtools_required_version  12.40

Summary:	Tools to configure the keyboard, the mice and the graphic card
Name:		drakx-kbd-mouse-x11
Version:	0.115
Release:	1
License:	GPLv2+
Group:		System/Configuration/Other
Url:		https://abf.rosalinux.ru/omv_software/drakx-kbd-mouse-x11
Source0:	%{name}-%{version}.tar.xz
BuildRequires:	gettext
BuildRequires:	perl-MDK-Common-devel
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(xxf86misc)
Requires:	drakxtools-curses => %drakxtools_required_version
Requires:	ldetect-lst >= 0.1.312
# need the common pam config files for usermode config
Requires:	usermode-consoleonly
%ifnarch %{sparcx} %{arm} %{mips}
Requires:	monitor-edid >= 1.12
%endif
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
%apply_patches

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
PROGRAM=%{_sbindir}/XFdrake
FALLBACK=false
SESSION=true
EOF

ln -s %{_sysconfdir}/security/console.apps/xfdrake \
        %{buildroot}%{_sysconfdir}/security/console.apps/XFdrake

# add nokmsboot if necessary and rebuild initrds so that they handle it
%triggerpostun -- drakx-kbd-mouse-x11 < 0.91
perl -I%{_prefix}/lib/libDrakX -MXconfig::various -e 'Xconfig::various::setup_kms();' &>/dev/null
%{_sbindir}/bootloader-config --action rebuild-initrds || :

%files -f %{name}.lang
%doc COPYING NEWS
%config(noreplace) %{_sysconfdir}/pam.d/xfdrake
%config(noreplace) %{_sysconfdir}/security/console.apps/xfdrake
# symlink
%{_sysconfdir}/security/console.apps/XFdrake
/sbin/display_driver_helper
%{_bindir}/XFdrake
%{_sbindir}/*
%{_datadir}/libDrakX/pixmaps/*
%{_prefix}/lib/libDrakX/auto/*
%{_prefix}/lib/libDrakX/xf86misc/main.pm
%{_prefix}/lib/libDrakX/Xconfig/*.pm
%dir %{_prefix}/lib/libDrakX/Xconfig
%{_prefix}/lib/libDrakX/*.pm
