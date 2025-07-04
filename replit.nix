
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.uvicorn
    pkgs.python311Packages.pydantic
    pkgs.python311Packages.jinja2
    pkgs.python311Packages.aiofiles
    pkgs.python311Packages.pillow
    pkgs.python311Packages.reportlab
    pkgs.python311Packages.transformers
    pkgs.python311Packages.torch
    pkgs.python311Packages.sqlite
  ];
}
