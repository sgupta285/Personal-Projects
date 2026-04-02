# Release Flow

1. Build application and bootloader binaries with deterministic flags.
2. Generate a manifest with checksums, sizes, and board metadata.
3. Package binaries and metadata into a release tarball with fixed timestamps.
4. Verify archive contents and checksum integrity.
5. Run a hardware integration handshake against the device simulator before promoting the build.
