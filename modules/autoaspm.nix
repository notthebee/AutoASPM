# NOTE: arguments passed from the flake directly
{
  self,
  ...
}:
{
  config,
  pkgs,
  lib,
  ...
}:
let
  cfg = config.services.autoaspm;
in
{
  options.services.autoaspm = {
    enable = lib.mkEnableOption "Automatically activate ASPM on all supported devices";
    package = lib.mkPackageOption self.packages.${pkgs.stdenv.hostPlatform.system} "autoaspm" { };
  };

  config = lib.mkIf cfg.enable {
    environment.systemPackages = [
      cfg.package
    ];

    systemd.services.autoaspm = {
      description = "Automatically activate ASPM on all supported devices";
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        Type = "oneshot";
        ExecStart = "${lib.getExe cfg.package}";
      };
    };
  };
}
