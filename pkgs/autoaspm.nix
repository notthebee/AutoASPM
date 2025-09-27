{
  stdenv,
  pkgs,
  ...
}:
stdenv.mkDerivation {
  name = "autoaspm";
  pname = "autoaspm";
  propagatedBuildInputs = [
    pkgs.pciutils
    pkgs.which
  ];
  dontUnpack = true;
  installPhase = "install -Dm755 ${./autoaspm.py} $out/bin/autoaspm";
}
