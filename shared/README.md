
# UNITY-Physics Utils

Shared utility functions, scripts, and tools used across UNITY-Physics projects and Docker containers.

This repository serves as a **single source of truth** for reusable components that are common to multiple codebases and analysis pipelines in the UNITY-Physics ecosystem.

---

## 📦 Contents

- General-purpose Python utility functions
- Data processing helpers
- Docker-friendly structure for easy inclusion

---

## 🚀 Usage

### 1. Clone Directly in Dockerfile

To include the latest version in a Docker image:

```dockerfile
RUN git clone --depth 1 https://github.com/UNITY-Physics/utils.git /app/shared
````

Or clone a specific tag:

```dockerfile
RUN git clone --branch v1.0.0 https://github.com/UNITY-Physics/utils.git /app/shared
```

---

### 2. As a Git Submodule

Add the utils as a submodule in your repo:

```bash
git submodule add https://github.com/UNITY-Physics/utils.git shared
```

Then in your Dockerfile:

```dockerfile
ENV FLYWHEEL="/flywheel/v0"
COPY shared/utils/ $FLYWHEEL/utils/
```

To update the submodule later:

```bash
git submodule update --remote --merge
```

---

### 3. As a Python Package (Optional)

If this repo is structured as a Python package (with `setup.py` or `pyproject.toml`):

```dockerfile
RUN pip install git+https://github.com/UNITY-Physics/utils.git@main
```

Or install a specific version:

```dockerfile
RUN pip install git+https://github.com/UNITY-Physics/utils.git@v1.0.0
```

---

## 🔄 Versioning & Updates

Please tag versions using Git:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Downstream projects should pin to specific tags for reproducibility.

---

## 🤝 Contributing

If you’d like to contribute new utilities or improve existing ones:

1. Fork this repository.
2. Make your changes in a feature branch.
3. Open a pull request with a clear description.

---

## 🧠 About UNITY-Physics

UNITY-Physics is an initiative to advance neuroimaging and medical physics research through collaborative, open-source tools and reproducible workflows.

For questions or support, contact the UNITY-Physics development team.

