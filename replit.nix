{pkgs}: {
  deps = [
    pkgs.libGLU
    pkgs.libGL
    pkgs.tesseract
    pkgs.postgresql
    pkgs.openssl
  ];
}
