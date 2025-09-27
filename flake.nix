{
  description = "Automatically enable ASPM on all supported PCIe devices";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      eachSystem = nixpkgs.lib.genAttrs systems;
    in
    {
      nixosModules = {
        autoaspm = import ./modules/autoaspm.nix { inherit self; };
        default = self.nixosModules.autoaspm;
      };
      packages = eachSystem (system: {
        default = self.packages.${system}.autoaspm;
        autoaspm = nixpkgs.legacyPackages.${system}.callPackage ./pkgs/autoaspm.nix { };
      });
    };
}
