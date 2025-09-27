{
  config,
  pkgs,
  lib,
  autoaspm,
  ...
}:
let
  cfg = config.services.autoaspm;
in
{
  options.services.autoaspm = {
    enable = lib.mkEnableOption "Automatically activate ASPM on all supported devices";
  };

  config = lib.mkIf cfg.enable {
    environment.systemPackages = [
      autoaspm
    ];
    systemd.services.autoaspm = {
      description = "Automatically activate ASPM on all supported devices";
      wantedBy = [ "multi-user.target" ];
      path = [
        pkgs.python313
        pkgs.which
        pkgs.pciutils
        autoaspm
      ];
      serviceConfig = {
        Type = "oneshot";
        ExecStart = "${lib.getExe pkgs.python313} ${autoaspm}/bin/autoaspm";
      };
    };
  };
}
