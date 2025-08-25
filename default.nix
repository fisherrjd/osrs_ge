{ pkgs ? import
    (fetchTarball {
      name = "jpetrucciani-2025-08-25";
      url = "https://github.com/jpetrucciani/nix/archive/0fe412941d3150472f59923093594afd1eac9d8a.tar.gz";
      sha256 = "0r319ri41zfmdvy6g9p5pdqwymvij7x0k56gvdikqn241c19hx5j";
    })
    { }
}:
let
  name = "osrs_ge";

  uvEnv = pkgs.uv-nix.mkEnv {
    inherit name; python = pkgs.python313;
    workspaceRoot = pkgs.hax.filterSrc { path = ./.; };
    pyprojectOverrides = final: prev: { };
  };

  tools = with pkgs; {
    cli = [
      jfmt
      nixup
    ];
    uv = [ uv uvEnv ];
    scripts = pkgs.lib.attrsets.attrValues scripts;
  };

  repo = "$(${pkgs.git}/bin/git rev-parse --show-toplevel)";

  scripts = with pkgs; {
    inherit (uvEnv.wrappers) black ruff ty;
    db = pkgs.pog {
      name = "db";
      script = ''
        ${uvEnv}/bin/python -m aggregator.db.data_input
      '';
    };
  };
  paths = pkgs.lib.flatten [ (builtins.attrValues tools) ];
  env = pkgs.buildEnv {
    inherit name paths; buildInputs = paths;
  };
in
(env.overrideAttrs (_: {
  inherit name;
  NIXUP = "0.0.9";
  shellHook = ''
    repo="${repo}"
    export PYTHONPATH="$repo:$PYTHONPATH"
    ln -sf ${uvEnv.uvEnvVars._UV_SITE} .direnv/site
  '';
} // uvEnv.uvEnvVars)) // { inherit scripts; }
