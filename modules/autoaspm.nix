{
  config,
  pkgs,
  lib,
  ...
}:
let
  cfg = config.services.auto-aspm;
in
{
  options.services.auto-aspm = {
    enable = lib.mkEnableOption "Automatically activate ASPM on all supported devices";
  };

  config = lib.mkIf cfg.enable {
    environment.systemPackages = [
      pkgs.autoaspm
    ];
    systemd.services.auto-aspm = {
      description = "Automatically activate ASPM on all supported devices";
      wantedBy = [ "multi-user.target" ];
      path = [
        pkgs.python313
        pkgs.which
        pkgs.pciutils
        pkgs.autoaspm
      ];
      serviceConfig = {
        Type = "oneshot";
        ExecStart = "${lib.getExe pkgs.python313} ${pkgs.autoaspm}/bin/autoaspm";
      };
    };
  };
}
