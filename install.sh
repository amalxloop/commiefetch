#!/bin/sh
# commiefetch install script

set -e

PREFIX="${1:-/usr/local}"
BINDIR="${DESTDIR}${PREFIX}/bin"

echo "☭  Installing commiefetch to ${BINDIR} ..."

mkdir -p "${BINDIR}"

cat > "${BINDIR}/commiefetch" << 'EOF'
#!/usr/bin/env python3
import sys
import os

script_dir = os.path.dirname(os.path.realpath(__file__))
# Try installed package first
try:
    from commiefetch.cli import main
except ImportError:
    # Fall back to source tree relative to this script
    src_dir = os.path.join(script_dir, "..", "lib", "commiefetch", "src")
    if os.path.isdir(src_dir):
        sys.path.insert(0, src_dir)
    else:
        # Try parent directory structure
        src_dir = os.path.join(script_dir, "..", "share", "commiefetch", "src")
        if os.path.isdir(src_dir):
            sys.path.insert(0, src_dir)
    from commiefetch.cli import main

sys.exit(main())
EOF

chmod +x "${BINDIR}/commiefetch"

# Copy source
SHARE_DIR="${DESTDIR}${PREFIX}/share/commiefetch"
mkdir -p "${SHARE_DIR}/src"
cp -r "$(dirname "$0")/src/commiefetch" "${SHARE_DIR}/src/commiefetch"

echo "☭  commiefetch installed successfully!"
echo "   Run 'commiefetch' to see your system info."
