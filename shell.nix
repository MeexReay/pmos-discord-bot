{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = with pkgs; [ 
    (python3.withPackages (libs: with libs; [
      discordpy
      requests
    ]))
  ];
}
