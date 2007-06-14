%define drakxtools_required_version  10.4.94-1mdv2007.0
%define drakxtools_conflicted_version  10.4.89

%define libname %mklibname %{name}

Summary:  Tools to configure the keyboard, the mice and the graphic card
Name:     drakx-kbd-mouse-x11
Version:  0.18
Release:  %mkrel 1
Source0:  %name-%version.tar.bz2
License:  GPL
Group:    System/Configuration/Other
Url:      http://www.mandrivalinux.com/en/cvs.php3
BuildRequires: perl-MDK-Common-devel gettext perl-devel
BuildRequires: libxxf86misc-devel ncurses-devel
Requires: drakxtools-curses => %drakxtools_required_version
%ifnarch %{sunsparc}
Requires: monitor-edid >= 1.5
%endif %{sunsparc}
BuildRoot: %_tmppath/%name-%version-buildroot
# for program:
Conflicts: drakxtools <= %drakxtools_conflicted_version
# for man pages:
Conflicts: drakxtools-curses <= %drakxtools_conflicted_version
# for Cards+ using nvidia97xx instead of nvidia, and nvidia71xx instead of NVIDIA_LEGACY:
Conflicts: ldetect-lst < 0.1.151

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

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root)
%doc COPYING NEWS
%_sbindir/*
%_datadir/libDrakX/pixmaps/*
/usr/lib/libDrakX/auto/*
/usr/lib/libDrakX/xf86misc/main.pm
/usr/lib/libDrakX/Xconfig/*.pm
/usr/lib/libDrakX/*.pm



