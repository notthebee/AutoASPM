{
  lib,
  stdenv,
  makeWrapper,
  pciutils,
  which,
  python3,
}:

stdenv.mkDerivation {
  pname = "autoaspm";
  version = "0.1";

  src = ./autoaspm.py;

  nativeBuildInputs = [ makeWrapper ];

  buildInputs = [
    pciutils
    which
  ];

  dontUnpack = true;

  installPhase = ''
    runHook preInstall

    install -Dm755 $src $out/libexec/autoaspm/autoaspm.py

    makeWrapper ${python3.interpreter} "$out/bin/autoaspm" \
      --add-flags "$out/libexec/autoaspm/autoaspm.py" \
      --prefix PATH : ${lib.makeBinPath [ pciutils which ]}

    runHook postInstall
  '';

  meta = {
    description = "Automatically enable ASPM on all supported PCIe devices";
    homepage = "https://github.com/notthebee/AutoASPM";
    platforms = lib.platforms.linux;
    mainProgram = "autoaspm";
  };
}
