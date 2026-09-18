.RECIPEPREFIX := >

#=============================================
# Config
#=============================================
EPICS_BASE = /epics/base
MODULES    = /epics/modules

EPICS_BASE_REPO = https://github.com/epics-base/epics-base.git
EPICS_BASE_TAG  = R7.0.10

SYNAPPS_CONFIG_REPO = https://github.com/EPICS-synApps/configure.git

#=============================================
# Helpers
#=============================================

# -------------------------------
define get_version
TMP=$$(mktemp -d); \
git clone --depth 1 $(SYNAPPS_CONFIG_REPO) $$TMP/configure >/dev/null; \
RELEASE=$$TMP/configure/RELEASE; \
RAW=$$(grep "^$(1)=" $$RELEASE | cut -d= -f2); \
CLEAN=$$(echo "$$RAW" | sed -E 's/\$\([A-Z_]+\)\///'); \
VER=$$(echo "$$CLEAN" | sed -E 's/^[^-]+-//'); \
rm -rf $$TMP; \
echo $$VER
endef
# -------------------------------

# -------------------------------
define ensure_tirpc
if [ ! -f /usr/include/tirpc/rpc/rpc.h ]; then \
  if command -v apt >/dev/null; then \
    sudo apt update && sudo apt install -y libtirpc-dev; \
  elif command -v dnf >/dev/null; then \
    sudo dnf install -y libtirpc-devel; \
  else \
    echo "Install libtirpc manually"; exit 1; \
  fi; \
fi
endef
# -------------------------------

# -------------------------------
define ensure_hdf5
if [ ! -f /usr/include/hdf5/serial/hdf5.h ]; then \
  if command -v apt >/dev/null; then \
    sudo apt update && sudo apt install -y libhdf5-dev; \
  elif command -v dnf >/dev/null; then \
    sudo dnf install -y hdf5-devel; \
  else \
    echo "Install HDF5 development package manually"; exit 1; \
  fi; \
fi
endef
# -------------------------------

# -------------------------------
define ensure_libxml2
if [ ! -f /usr/include/libxml2/libxml/parser.h ]; then \
  if command -v apt >/dev/null; then \
    sudo apt update && sudo apt install -y libxml2-dev; \
  elif command -v dnf >/dev/null; then \
    sudo dnf install -y libxml2-devel; \
  else \
    echo "Install libxml2 development package manually"; exit 1; \
  fi; \
fi
endef
# -------------------------------

# -------------------------------
# Workaround for _FORTIFY_SOURCE=3 only needed on R7.0.8 and earlier.
# R7.0.9+ includes the upstream fix (PR #517).
define fix_fortify_source
MAJMIN=$$(echo $(EPICS_BASE_TAG) | sed -E 's/^R//;s/\.[0-9]+$$//'); \
PATCH=$$(echo $(EPICS_BASE_TAG) | sed -E 's/^R[0-9]+\.[0-9]+\.//'); \
if [ "$$MAJMIN" = "7.0" ] && [ "$$PATCH" -le 8 ] 2>/dev/null; then \
  CFGFILE=$(EPICS_BASE)/configure/os/CONFIG_SITE.linux-x86_64.linux-x86_64; \
  if [ -f "$$CFGFILE" ] && ! grep -q 'FORTIFY_SOURCE' "$$CFGFILE"; then \
    echo "" >> "$$CFGFILE"; \
    echo "# Workaround: _FORTIFY_SOURCE=3 (GCC 14 / Ubuntu 24.04 default)" >> "$$CFGFILE"; \
    echo "# misidentifies EPICS record-type upcasts as buffer overflows." >> "$$CFGFILE"; \
    echo "# Fixed upstream in epics-base PR #517 (post-R7.0.8)." >> "$$CFGFILE"; \
    echo "USR_CFLAGS   += -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=2" >> "$$CFGFILE"; \
    echo "USR_CXXFLAGS += -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=2" >> "$$CFGFILE"; \
  fi; \
fi
endef
# -------------------------------

# -------------------------------
define build_base
set -e; \
mkdir -p $(dir $(EPICS_BASE)); \
if [ ! -f "$(EPICS_BASE)/configure/RULES_TOP" ]; then \
  rm -rf "$(EPICS_BASE)"; \
  git clone --depth 1 --branch $(EPICS_BASE_TAG) $(EPICS_BASE_REPO) $(EPICS_BASE); \
fi; \
$(call fix_fortify_source); \
if [ ! -f "$(EPICS_BASE)/lib/libCom.so" ]; then \
  make -C $(EPICS_BASE) -j; \
fi
endef
# -------------------------------

# -------------------------------
define build_asyn
set -e; \
mkdir -p $(MODULES); \
$(call ensure_tirpc); \
ASYN=$$($(call get_version,ASYN)); \
echo "Using ASYN=$$ASYN"; \
if [ ! -d "$(MODULES)/asyn" ]; then \
  git clone --depth 1 --branch $$ASYN https://github.com/epics-modules/asyn.git $(MODULES)/asyn; \
fi; \
echo "EPICS_BASE=$(EPICS_BASE)" > $(MODULES)/asyn/configure/RELEASE.local; \
mkdir -p $(MODULES)/asyn/configure; \
echo "USR_CPPFLAGS += -I/usr/include/tirpc" >> $(MODULES)/asyn/configure/CONFIG_SITE; \
echo "USR_SYS_LIBS += tirpc" >> $(MODULES)/asyn/configure/CONFIG_SITE; \
sed -i "/test.*App/d" $(MODULES)/asyn/Makefile || true; \
make -C $(MODULES)/asyn -j; \
make -C $(MODULES)/asyn
endef
# -------------------------------

# -------------------------------
define build_autosave
set -e; \
AUTOSAVE=$$($(call get_version,AUTOSAVE)); \
echo "Using AUTOSAVE=$$AUTOSAVE"; \
if [ ! -d "$(MODULES)/autosave" ]; then \
  git clone --depth 1 --branch $$AUTOSAVE https://github.com/epics-modules/autosave.git $(MODULES)/autosave; \
fi; \
echo "EPICS_BASE=$(EPICS_BASE)" > $(MODULES)/autosave/configure/RELEASE.local; \
echo "SUPPORT="                 >> $(MODULES)/autosave/configure/RELEASE.local; \
make -C $(MODULES)/autosave -j; \
make -C $(MODULES)/autosave
endef
# -------------------------------

# -------------------------------
define build_busy
set -e; \
BUSY=$$($(call get_version,BUSY)); \
echo "Using BUSY=$$BUSY"; \
if [ ! -d "$(MODULES)/busy" ]; then \
  git clone --depth 1 --branch $$BUSY https://github.com/epics-modules/busy.git $(MODULES)/busy; \
fi; \
echo "EPICS_BASE=$(EPICS_BASE)"          > $(MODULES)/busy/configure/RELEASE.local; \
echo "ASYN=$(MODULES)/asyn"             >> $(MODULES)/busy/configure/RELEASE.local; \
echo "AUTOSAVE=$(MODULES)/autosave"     >> $(MODULES)/busy/configure/RELEASE.local; \
echo "SUPPORT="                          >> $(MODULES)/busy/configure/RELEASE.local; \
echo "BUSY=$(MODULES)/busy"             >> $(MODULES)/busy/configure/RELEASE.local; \
grep -q 'CHECK_RELEASE' $(MODULES)/busy/configure/RELEASE 2>/dev/null || \
  echo "CHECK_RELEASE = NO" >> $(MODULES)/busy/configure/CONFIG_SITE; \
make -C $(MODULES)/busy -j; \
make -C $(MODULES)/busy
endef
# -------------------------------

# -------------------------------
define build_sscan
set -e; \
SSCAN=$$($(call get_version,SSCAN)); \
echo "Using SSCAN=$$SSCAN"; \
if [ ! -d "$(MODULES)/sscan" ]; then \
  git clone --depth 1 --branch $$SSCAN https://github.com/epics-modules/sscan.git $(MODULES)/sscan; \
fi; \
echo "EPICS_BASE=$(EPICS_BASE)" > $(MODULES)/sscan/configure/RELEASE.local; \
echo "SUPPORT="                 >> $(MODULES)/sscan/configure/RELEASE.local; \
echo "SNCSEQ="                  >> $(MODULES)/sscan/configure/RELEASE.local; \
sed -i '1i #include <shareLib.h>' $(MODULES)/sscan/sscanApp/src/saveData_writeXDR.c 2>/dev/null || true; \
make -C $(MODULES)/sscan -j; \
make -C $(MODULES)/sscan
endef
# -------------------------------

# -------------------------------
define build_calc
set -e; \
CALC=$$($(call get_version,CALC)); \
echo "Using CALC=$$CALC"; \
if [ ! -d "$(MODULES)/calc" ]; then \
  git clone --depth 1 --branch $$CALC https://github.com/epics-modules/calc.git $(MODULES)/calc; \
fi; \
echo "EPICS_BASE=$(EPICS_BASE)" > $(MODULES)/calc/configure/RELEASE.local; \
echo "SSCAN=$(MODULES)/sscan"   >> $(MODULES)/calc/configure/RELEASE.local; \
echo "SUPPORT="                 >> $(MODULES)/calc/configure/RELEASE.local; \
echo "SNCSEQ="                  >> $(MODULES)/calc/configure/RELEASE.local; \
make -C $(MODULES)/calc -j; \
make -C $(MODULES)/calc
endef
# -------------------------------

# -------------------------------
define build_ad
set -e; \
$(call ensure_hdf5); \
$(call ensure_libxml2); \
AD=$$($(call get_version,AREA_DETECTOR)); \
echo "Using ADCore=$$AD"; \
if [ ! -d "$(MODULES)/ADCore" ]; then \
  git clone --depth 1 --branch $$AD https://github.com/areaDetector/ADCore.git $(MODULES)/ADCore; \
fi; \
echo "EPICS_BASE=$(EPICS_BASE)"     > $(MODULES)/ADCore/configure/RELEASE.local; \
echo "ASYN=$(MODULES)/asyn"        >> $(MODULES)/ADCore/configure/RELEASE.local; \
CFGSITE=$(MODULES)/ADCore/configure/CONFIG_SITE; \
if ! grep -q 'WITH_HDF5' "$$CFGSITE" 2>/dev/null; then \
  echo ""                                        >> "$$CFGSITE"; \
  echo "# HDF5 plugin support (system libhdf5-dev)" >> "$$CFGSITE"; \
  echo "WITH_HDF5     = YES"                     >> "$$CFGSITE"; \
  echo "HDF5_EXTERNAL = YES"                     >> "$$CFGSITE"; \
  if [ -d /usr/include/hdf5/serial ]; then \
    echo "HDF5_INCLUDE  = /usr/include/hdf5/serial"           >> "$$CFGSITE"; \
    echo "HDF5_LIB      = /usr/lib/x86_64-linux-gnu/hdf5/serial" >> "$$CFGSITE"; \
  fi; \
  echo "WITH_NETCDF  = NO"  >> "$$CFGSITE"; \
  echo "WITH_NEXUS   = NO"  >> "$$CFGSITE"; \
  echo "WITH_TIFF    = NO"  >> "$$CFGSITE"; \
  echo "WITH_JPEG    = NO"  >> "$$CFGSITE"; \
  echo "WITH_SZIP    = NO"  >> "$$CFGSITE"; \
  echo "WITH_BLOSC   = NO"  >> "$$CFGSITE"; \
  echo "WITH_BITSHUFFLE = NO" >> "$$CFGSITE"; \
  echo "WITH_GRAPHICSMAGICK = NO" >> "$$CFGSITE"; \
fi; \
if ! grep -q '^XML2_EXTERNAL' "$$CFGSITE" 2>/dev/null; then \
  echo "XML2_EXTERNAL = YES" >> "$$CFGSITE"; \
fi; \
if ! grep -q '^XML2_INCLUDE' "$$CFGSITE" 2>/dev/null; then \
  echo "XML2_INCLUDE = /usr/include/libxml2" >> "$$CFGSITE"; \
fi; \
PLUGMK=$(MODULES)/ADCore/ADApp/pluginSrc/Makefile; \
sed -i 's/-DH5_NO_DEPRECATED_SYMBOLS -DH5Gopen_vers=2/-DH5Gopen_vers=2/' "$$PLUGMK" || true; \
make -C $(MODULES)/ADCore -j; \
make -C $(MODULES)/ADCore
endef
# -------------------------------

# -------------------------------
define build_motor
set -e; \
MOTOR=$$($(call get_version,MOTOR)); \
echo "Using MOTOR=$$MOTOR"; \
if [ ! -d "$(MODULES)/motor" ]; then \
  git clone --depth 1 --branch $$MOTOR https://github.com/epics-modules/motor.git $(MODULES)/motor; \
fi; \
sed -i '1i #include <shareLib.h>' $(MODULES)/motor/motorApp/MotorSrc/motordrvCom.h; \
sed -i '/^IPAC/d' $(MODULES)/motor/configure/RELEASE; \
sed -i '/^SNCSEQ/d' $(MODULES)/motor/configure/RELEASE; \
sed -i '/^SUPPORT/d' $(MODULES)/motor/configure/RELEASE; \
rm -rf $(MODULES)/motor/modules/motor* || true; \
sed -i "/^SUBMODULES/d" $(MODULES)/motor/modules/Makefile || true; \
sed -i "/ifdef IPAC/,/endif/d" $(MODULES)/motor/modules/Makefile || true; \
sed -i "/ifdef MX/,/endif/d" $(MODULES)/motor/modules/Makefile || true; \
sed -i "/ifdef LUA/,/endif/d" $(MODULES)/motor/modules/Makefile || true; \
echo "EPICS_BASE=$(EPICS_BASE)" > $(MODULES)/motor/configure/RELEASE.local; \
echo "ASYN=$(MODULES)/asyn" >> $(MODULES)/motor/configure/RELEASE.local; \
make -C $(MODULES)/motor -j; \
make -C $(MODULES)/motor
endef
# -------------------------------

#=============================================
# Targets (clean & explicit)
#=============================================

.PHONY: base asyn autosave busy sscan calc ad motor clean

base:
> $(build_base)

asyn: base
> $(build_asyn)

autosave: base
> $(build_autosave)

busy: asyn autosave
> $(build_busy)

sscan: base
> $(build_sscan)

calc: sscan
> $(build_calc)

ad: asyn busy sscan calc autosave
> $(build_ad)

motor: asyn
> $(build_motor)

clean:
> rm -rf $(MODULES)

