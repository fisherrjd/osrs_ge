{ pkgs ? import
    (fetchTarball {
      name = "jpetrucciani-2025-11-26";
      url = "https://github.com/jpetrucciani/nix/archive/e2f539f2a618c4b07bc9f45efb71c8038f779f05.tar.gz";
      sha256 = "0m48y4gsqm0vfx0v1yglsm8fb6zw8y0d711q5mzqc3pqxmlliyr4";
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
    db = [ duckdb];
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
