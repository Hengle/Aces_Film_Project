# Mantra

The way renderers work is that they can't read the 3D package data natively, all that data needs to get converted to another format that the renderer can parse. In Mantras case, it's IFD. In Redshift, it's .rs files. In Karma's case, it's USD. So whenever you start a render on a larger seen, you know how that's that long pause before the first pixel renders? That's when the renderer translates your scene to its preferred scene file

But what that means is that whenever you start a mantra render, for example, an IFD files is created and stored... somewhere.

Okay so we just create an environment variable to a folder within the project to hold our IFDs, and the HQueue node already has a toggle for saving out those IFDs to disk. If I had to guess they probably don't leave RAM unless you tell it to otherwise.

---

Hopefully we will get to use the Deadline renderfarm on campus. See link below for more info

[[Deadline Render farm]]


---

# Formats

always render out EXRs.

- higher dynamic range
- build in AOVs


---

