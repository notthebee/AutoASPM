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
  };

  config = lib.mkIf cfg.enable {
    environment.systemPackages = [
      pkgs.autoaspm
    ];
    systemd.services.autoaspm = {
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
