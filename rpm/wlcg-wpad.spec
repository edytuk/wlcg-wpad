Summary: WLCG Web Proxy Auto Discovery
Name: wlcg-wpad
Version: 1.11
Release: 1%{?dist}
BuildArch: noarch
Group: Applications/System
License: BSD
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Source0: https://frontier.cern.ch/dist/%{name}-%{version}.tar.gz

Requires: httpd
Requires: mod_wsgi
Requires: cvmfs-server >= 2.5.1
Requires: python-anyjson
Requires: python-netaddr

%description
Supplies Web Proxy Auto Discovery information for the Worldwide
LHC Computing Grid at URL http://wlcg-wpad.cern.ch/wpad.dat

%prep
%setup -q

%install
mkdir -p $RPM_BUILD_ROOT/etc/cron.d
install -p -m 444 misc/wlcg-wpad.cron $RPM_BUILD_ROOT/etc/cron.d/wlcg-wpad
mkdir -p $RPM_BUILD_ROOT/etc/httpd/conf.d
install -p -m 444 misc/wlcg-wpad.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/10-wlcg-wpad.conf
install -p -m 444 misc/geoapi.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/11-geoapi.conf
mkdir -p $RPM_BUILD_ROOT/var/www/wsgi-scripts/wlcg-wpad
install -p -m 555 misc/wlcg-wpad.wsgi $RPM_BUILD_ROOT/var/www/wsgi-scripts/wlcg-wpad
mkdir -p $RPM_BUILD_ROOT/usr/share/wlcg-wpad/pyweb
install -p -m 555 misc/sync_wpad_conf $RPM_BUILD_ROOT/usr/share/wlcg-wpad
mkdir -p $RPM_BUILD_ROOT/usr/share/wlcg-wpad/pyweb
install -p -m 444 pyweb/* $RPM_BUILD_ROOT/usr/share/wlcg-wpad/pyweb
mkdir -p $RPM_BUILD_ROOT/var/lib/wlcg-wpad

%post
cvmfs_server update-geodb
/usr/share/wlcg-wpad/sync_wpad_conf
/sbin/service httpd status >/dev/null && /sbin/service httpd reload
:

%postun
if [ $1 = 0 ]; then
    rm -rf /var/lib/wlcg-wpad
fi

%files
/etc/cron.d/*
/etc/httpd/conf.d/*
/var/www/wsgi-scripts/wlcg-wpad
/usr/share/wlcg-wpad
/var/lib/wlcg-wpad


%changelog
* Fri May 24 2019 Dave Dykstra <dwd@fnal.gov> 1.11-1
- Reorganize log messages for easier kibana monitor parsing.

* Tue Nov  5 2018 Dave Dykstra <dwd@fnal.gov> 1.10-1
- Add support for the OVERLOAD special proxy selection function and the
  overload excludes option.
- Fix the locks on reading worker-proxies.json and wlcgwpad.conf.
- Update to GeoIP2 databases, require cvmfs-server >= 2.5.1

* Fri Sep 14 2018 Dave Dykstra <dwd@fnal.gov> 1.9-1
- Add support for unquoting the ? parameter.  This is so an '=' can be
  hidden from the frontier client with %3d.

* Tue Aug 21 2018 Dave Dykstra <dwd@fnal.gov> 1.8-1
- Require cvmfs-server <= 2.5.0.  2.5.1 has an incompatible geo db.

* Sun Aug 19 2018 Dave Dykstra <dwd@fnal.gov> 1.7-1
- Add support for the cvmfs geoapi, for stashcp.

* Fri Jul 27 2018 Dave Dykstra <dwd@fnal.gov> 1.6-1
- If no proxies are specified in hostproxies after a destination alias,
  make the response return NONE as a default.  That causes frontier to
  give a fatal error if it hits the case, which is what I want, but
  cvmfs skips past it (although it logs some nasty-looking error
  messages).  Cvmfs will not connect to the server however without a
  DIRECT proxy so it will still fail too.

* Mon Feb 19 2018 Dave Dykstra <dwd@fnal.gov> 1.5-1
- Add rsync timeouts to prevent it from hanging indefinitely.

* Wed Dec 06 2017 Dave Dykstra <dwd@fnal.gov> - 1.4-1
- Add support for backupproxies including WLCG+BACKUP in wlcgwpad.conf.

* Wed Nov 29 2017 Dave Dykstra <dwd@fnal.gov> - 1.3-1
- Update worker proxies from scratch instead of modifying in place.  This
  enables removed sites to be deleted.
- Update configuration and worker proxies in separate space so the updates
  are atomic to other threads.

* Wed Nov 15 2017 Dave Dykstra <dwd@fnal.gov> - 1.2-1
- Lock the updates of reading config files, so only one thread ever does it.
- Remove tabs from source files.

* Thu Nov 02 2017 Dave Dykstra <dwd@fnal.gov> - 1.1-1
- Re-read wlcgpad.conf if it changes.  Check every 5 minutes, just like
  worker-proxies.json already was.

* Wed Nov 01 2017 Dave Dykstra <dwd@fnal.gov> - 1.0-1
- Add support for destination aliases in hostproxies
- Add support for DIRECT proxy
- Change WSGI config to be like the latest cvmfs-server

* Thu Oct 06 2016 Dave Dykstra <dwd@fnal.gov> - 0.9-1
- Add log message when geosorted squids are returned

* Fri Sep 30 2016 Dave Dykstra <dwd@fnal.gov> - 0.8-1
- Fix bug with the ipranges implementation

* Fri Sep 30 2016 Dave Dykstra <dwd@fnal.gov> - 0.7-1
- Change config file name from geosort.conf to wlcgwpad.conf
- Add support for destshexps config variable, which are shortcuts to shell
  expressions that choose different proxy services
- Add support for ipranges keyword in input file, to limit a proxy service
  to a subrange of source addresses
- Use ip address passed in from input file instead of looking names up
  in the DNS

* Tue Sep 20 2016 Dave Dykstra <dwd@fnal.gov> - 0.6-1
- Return specific error messages from wlcg_wpad module to the user
  rather than a generic "No proxy found"

* Tue Sep 20 2016 Dave Dykstra <dwd@fnal.gov> - 0.5-1
- Add support for client load balancing of proxies
- If "cmsnames" is present in the data, add those to the first line comment
  in the form "; CMS: sitename,..."

* Wed Aug 03 2016 Dave Dykstra <dwd@fnal.gov> - 0.4-1
- Disable the entries that are marked "disabled"
- When there's a match, print "// For sitename, ..." as a leading comment

* Wed Aug 03 2016 Dave Dykstra <dwd@fnal.gov> - 0.3-1
- Convert to reading from worker-proxies.json instead of grid-squids.json

* Fri Jun 03 2016 Dave Dykstra <dwd@fnal.gov> - 0.2-1
- Add initial implementation of wlcg-wpad.cern.ch
- Copy config files from wlcg-squid-monitor.cern.ch
- Rename apache config to 10-wlcg-wpad.conf to give it order priority

* Wed Apr 22 2016 Dave Dykstra <dwd@fnal.gov> - 0.1-1
- Initial version
