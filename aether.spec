%global pkg_name aether
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

# Conditionals to build Aether with or without AHC connector
# (connector for Async Http Client).
%if 0%{?fedora}
%bcond_without ahc
%endif

Name:           %{?scl_prefix}%{pkg_name}
Version:        1.13.1
Release:        13.11%{?dist}
Summary:        Sonatype library to resolve, install and deploy artifacts the Maven way
License:        EPL or ASL 2.0
URL:            https://docs.sonatype.org/display/AETHER/Home
# git clone https://github.com/sonatype/sonatype-aether.git
# git archive --prefix="aether-1.11/" --format=tar aether-1.11 | bzip2 > aether-1.11.tar.bz2
Source0:        %{pkg_name}-%{version}.tar.bz2
Source1:        http://www.apache.org/licenses/LICENSE-2.0.txt
Source2:        http://www.eclipse.org/legal/epl-v10.html
BuildArch:      noarch

BuildRequires:  %{?scl_prefix_java_common}maven-local
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven.wagon:wagon-provider-api)
BuildRequires:  %{?scl_prefix}mvn(org.codehaus.plexus:plexus-classworlds)
BuildRequires:  %{?scl_prefix}mvn(org.codehaus.plexus:plexus-component-annotations)
BuildRequires:  %{?scl_prefix}mvn(org.codehaus.plexus:plexus-component-metadata)
BuildRequires:  %{?scl_prefix}mvn(org.codehaus.plexus:plexus-utils)
BuildRequires:  %{?scl_prefix_java_common}mvn(org.slf4j:slf4j-api)
BuildRequires:  %{?scl_prefix}mvn(org.sonatype.forge:forge-parent:pom:)
BuildRequires:  %{?scl_prefix}mvn(org.sonatype.sisu:sisu-inject-plexus)
%if %{with ahc}
BuildRequires:  %{?scl_prefix}mvn(com.ning:async-http-client)
%endif

%description
Aether is a standalone library to resolve, install and deploy artifacts
the Maven way.

%package api
Summary: Aether API

%description api
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package provides application
programming interface for Aether repository system.

%if %{with ahc}
%package connector-asynchttpclient
Summary: Aether connector for Async Http Client

%description connector-asynchttpclient
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package provides Aether repository
connector implementation based on Async Http Client.
%endif

%package connector-file
Summary: Aether connector for file URLs

%description connector-file
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package provides Aether repository
connector implementation for repositories using file:// URLs.

%package connector-wagon
Summary: Aether connector for Maven Wagon

%description connector-wagon
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package provides Aether repository
connector implementation based on Maven Wagon.

%package impl
Summary: Implementation of Aether repository system

%description impl
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package provides implementation of
Aether repository system.

%package spi
Summary: Aether SPI

%description spi
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package contains Aether service
provider interface (SPI) for repository system implementations and
repository connectors.

%package test-util
Summary: Aether test utilities

%description test-util
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package provides collection of utility
classes that ease testing of Aether repository system.

%package util
Summary: Aether utilities

%description util
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package provides a collection of
utility classes to ease usage of Aether repository system.

%package javadoc
Summary: Java API documentation for Aether

%description javadoc
Aether is a standalone library to resolve, install and deploy
artifacts the Maven way.  This package provides Java API documentation
for Aether.

%prep
%setup -q -n %{pkg_name}-%{version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
cp -p %{SOURCE1} LICENSE-ASL
cp -p %{SOURCE2} LICENSE-EPL

%if %{without ahc}
%pom_disable_module aether-connector-asynchttpclient
%endif

# we'd need org.sonatype.http-testing-harness so let's remove async
# and wagon http tests (leave others enabled)
for module in asynchttpclient wagon; do (
    cd ./aether-connector-$module
    rm -rf src/test
    # Removes all dependencies with test scope
    %pom_xpath_remove "pom:dependency[pom:scope[text()='test']]"
) done

# Remove clirr plugin
%pom_remove_plugin :clirr-maven-plugin
%pom_remove_plugin :clirr-maven-plugin aether-api
%pom_remove_plugin :clirr-maven-plugin aether-spi

# Animal sniffer is not useful in Fedora
for module in . aether-connector-wagon aether-util aether-api   \
              aether-impl aether-connector-asynchttpclient      \
              aether-connector-file aether-demo aether-test-util; do
    %pom_remove_plugin :animal-sniffer-maven-plugin $module
done

# Workaround for rhbz#911365
%pom_xpath_inject pom:project "<dependencies/>"
%pom_add_dep cglib:cglib:any:test

# Keep compatibility with packages that use old JAR locations until
# they migrate.
%mvn_file ":{%{pkg_name}-{*}}" %{pkg_name}/@1 %{pkg_name}/@2
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%mvn_build -s
%{?scl:EOF}

%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%mvn_install
%{?scl:EOF}

%files -f .mfiles-%{pkg_name}
%doc README.md
%doc LICENSE-ASL LICENSE-EPL

%files api -f .mfiles-%{pkg_name}-api
%doc README.md
%doc LICENSE-ASL LICENSE-EPL
%dir %{_mavenpomdir}/%{pkg_name}
%dir %{_javadir}/%{pkg_name}

%files connector-file -f .mfiles-%{pkg_name}-connector-file
%files connector-wagon -f .mfiles-%{pkg_name}-connector-wagon
%files impl -f .mfiles-%{pkg_name}-impl
%files spi -f .mfiles-%{pkg_name}-spi
%files test-util -f .mfiles-%{pkg_name}-test-util
%files util -f .mfiles-%{pkg_name}-util
%files javadoc -f .mfiles-javadoc
%doc LICENSE-ASL LICENSE-EPL

%if %{with ahc}
%files connector-asynchttpclient -f .mfiles-%{pkg_name}-connector-asynchttpclient
%endif

%changelog
* Thu Jan 15 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-13.11
- Add directory ownership on %%{_mavenpomdir} subdir

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 1.13.1-13.10
- Mass rebuild 2015-01-13

* Mon Jan 12 2015 Michael Simacek <msimacek@redhat.com> - 1.13.1-13.9
- Rebuild to regenerate requires from java-common

* Tue Jan 06 2015 Michael Simacek <msimacek@redhat.com> - 1.13.1-13.8
- Mass rebuild 2015-01-06

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-13.7
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-13.6
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-13.5
- Mass rebuild 2014-02-18

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-13.4
- Add missing BR: plexus-component-metadata

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-13.3
- SCL-ize requires and build-requires

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-13.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-13.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.13.1-13
- Mass rebuild 2013-12-27

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-12
- Install license files
- Resolves: rhbz#958117

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-11
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Fri May 10 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-10
- Conditionally build without AHC connector

* Thu May  2 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-9
- Install compat JAR symlinks
- Resolves: rhbz#958558

* Tue Apr 30 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-8
- Complete spec file rewrite
- Build with xmvn
- Split into multiple subpackages, resolves: rhbz#916142
- Update to current packaging guidelines

* Thu Feb  7 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-7
- Build with xmvn
- Disable animal sniffer
- Remove R on jboss-parent, resolves: rhbz#908583

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 1.13.1-6
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Aug 27 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-5
- Disable animal-sniffer on RHEL

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.13.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jun 28 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.13.1-3
- Replace pom.xml patches with pom macros

* Thu Apr 19 2012 Alexander Kurtakov <akurtako@redhat.com> 1.13.1-2
- Install aether-connector-asynchttpclient - it was build but not installed.

* Tue Jan 31 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.13.1-1
- Update to latest upstream
- Update spec to latest guidelines

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.11-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Jun 8 2011 Alexander Kurtakov <akurtako@redhat.com> 1.11-3
- Build with maven 3.x.
- Do not require maven - not found in dependencies in poms.
- Guidelines fixes.

* Mon Feb 28 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.11-2
- Rebuild after bugfix update to plexus-containers (#675865)

* Fri Feb 25 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.11-1
- Update to latest version
- Add ASL 2.0 back as optional license

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jan 19 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.9-1
- License changed to EPL
- Add async-http-client to BR/R
- Update to latest version

* Wed Dec  8 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.7-3
- Make jars/javadocs versionless
- Remove buildroot and clean section

* Wed Oct 13 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.7-2
- Explained how to get tarball properly
- Removed noreplace on depmap fragment

* Mon Oct 11 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.7-1
- Initial Package
