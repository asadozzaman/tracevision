# Phase 1 dataset review — 2026-10-07

**Decision: no dataset accepted yet. Phase 1 is incomplete.**
This review uses author/project sources and observed access, not mirrors.
Published dataset descriptions below are source claims, not measurements by
TraceVision. No road images, video, or object ground truth have been inspected.
Only SVMOT release metadata has been downloaded and checked locally.

## Consistent comparison

All candidates are assessed for provenance, use and redistribution terms,
working access, temporal/identity annotations, event relevance, storage, and
free-compute feasibility. A recent publication alone is not an advantage.

| Dataset | Official provenance | License and redistribution | Access observed in this session |
| --- | --- | --- | --- |
| ROAD-Waymo (2024 preprint) | [Author repository](https://github.com/salmank255/Road-waymo-dataset), linked to Waymo community contributions | [Waymo March 2025 terms](https://waymo.com/open/terms/): noncommercial research/personal experimentation; dataset redistribution limited to registered recipients; trained-model distribution also restricted. Production use is restricted, including some unpaid services. Source-code MIT does not remove these terms. | Author instructions verified. Official download redirects to Google sign-in. No authenticated download or bytes verified. |
| TUMTraf-A (2025) | [Accident project](https://tum-traffic-dataset.github.io/tumtraf-a/), [paper](https://arxiv.org/abs/2508.14567), [publisher portal](https://innovation-mobility.com/en/project-providentia/a9-dataset/) | Accident project explicitly declares CC BY-NC-SA 4.0: attribution, noncommercial use, share-alike for distributed adaptations. Verify actual release terms; do not substitute a different TUMTraf release's license. | Registration is the advertised route. Direct dataset portal failed here. Accident release links and inventory not obtained. |
| TrafficMOT (ACM MM 2024) | [Author repository](https://github.com/lihaoliu-cambridge/trafficmot) and [paper](https://arxiv.org/abs/2311.18839) | No explicit dataset license or redistribution grant found in the inspected repository. Citation is not a license. Terms inside the archive remain unknown. | Author README now links a [Google Drive folder](https://drive.google.com/drive/folders/16h6P3oiMDtq3BtoT6rWdDz9rHnn3qBv7). A blank rendered folder does not establish file access. No bytes inspected. |
| ROAD (2022) | [Author repository](https://github.com/gurkirt/road-dataset); Oxford RobotCar-derived video | README declares CC BY-NC-SA 4.0 and noncommercial academic use. Video and event annotations have separate contacts for commercial permission; preserve attribution and upstream privacy conditions. | Author download script and links verified. A direct request to the script's annotation URL timed out. No video or annotation validated. |
| KITTI tracking (2013) | [Official tracking benchmark](https://www.cvlibs.net/datasets/kitti/eval_tracking.php) | [Official copyright page](https://www.cvlibs.net/datasets/kitti/) declares CC BY-NC-SA 3.0. Academic use, attribution, no commercial use, share-alike for distributed adaptations. | Current tracking page links login. A [legacy official download form](https://www.cvlibs.net/download.php?file=data_tracking_image_2.zip) requests email. No form submitted. A legacy S3 label object's HEAD returned 200; image HEAD timed out. S3 headers alone do not verify provenance, archive integrity, or usable data. |
| SVMOT v1.0 (July 2026) | [Author Zenodo DOI release](https://zenodo.org/records/19468203), MIPT creators | [Author record API](https://zenodo.org/api/records/19468203) declares `cc-by-nc-4.0` and open access. Attribution and noncommercial use; not unrestricted commercial data. The rendered page's license field was empty, so the structured record was checked. | Record, release SHA256SUMS, train/test lists and scene mapping retrieved. Three metadata files match release SHA-256s. Main archive range requests timed out; README download also failed. No image/ground-truth validation. |
| BDD100K (2020) | [Official toolkit](https://github.com/bdd100k/bdd100k) and linked Berkeley portal | Toolkit BSD-3-Clause is **not** the data license. [Maintainer clarification](https://github.com/bdd100k/bdd100k/discussions/130) says the dataset has separate terms. Current data terms and redistribution permission were not successfully retrieved. | Official Berkeley portal and data documentation could not be retrieved by the research tool. This corroborates a session access problem, not a permanent worldwide outage. No mirror adopted. |

| Dataset | Video and identity annotations | Event relevance | Storage evidence | CPU / free-compute assessment (inference, not a measurement) |
| --- | --- | --- | --- | --- |
| ROAD-Waymo | Author reports front-camera clips, boxes and tube IDs; about 20-second clips | Agent/action/location labels and their combinations directly support event research | Full/subset archive sizes not verified; author reports 1,000 videos | Selected clips should be practical; first establish authenticated per-file access. Full video-model training is outside free-compute planning. |
| TUMTraf-A | Project describes synchronized roadside RGB/LiDAR, trajectories and track IDs in OpenLABEL | Ten real accident sequences; strong accident relevance, narrow scene diversity | Accident archive size unresolved; general portal totals must not be treated as accident-release size | RGB-only subset could be practical; multi-sensor conversion and annotation version reconciliation add work. Split by accident, not camera or frame. |
| TrafficMOT | Paper concerns multi-object traffic tracking; actual frame/identity schema not inspected | Complex traffic tracking; no verified event ground truth in downloaded data | Archive size and smallest downloadable unit unresolved | Cannot budget reliably before inventory and license inspection. |
| ROAD | Author describes driving video, per-box tube IDs, actions, locations and ego actions | Strong integrated detection/tracking/event fit | Exact archive bytes unverified; author reports 22 long videos | Small continuous clips could suit CPU preparation and later free-GPU inference. Preserve official splits and source-drive groups. |
| KITTI tracking | 21 training and 29 test sequences; identity tracklets and occlusion/truncation; public training labels | Useful tracking and occlusion baseline; not labeled accident/action ground truth | Official page advertises 15 GB left images and 9 MB labels; these are page estimates, not measured downloads | RGB-only subset practical after acquisition; local evaluation needs a declared holdout from labeled training sequences. Hidden official test labels cannot be invented. |
| SVMOT | Author reports MOT-style frames/IDs, visibility, pairwise occlusion, depth order and stopped attributes | Particularly useful for stopped vehicles and identity recovery through occlusion; not a general accident benchmark | Record lists one 18,336,278,868-byte ZIP; extracted size unmeasured | Small scene-separated subset potentially practical, but full download needs adequate disk and reliable transfer. Scene mapping makes leakage control concrete. |
| BDD100K | Official toolkit describes driving videos and separate tracking tasks; keyframe detection data must not be mistaken for dense identity labels | Broad driving diversity; event supervision must be checked for the chosen release | Needed tracking archive sizes unresolved here; 100K-video headline does not define the development footprint | Feasible only with a verified small tracking release; full dataset is unnecessary. |

## Decision and outstanding questions

Original ROAD is the best **scope-fit candidate** for joint tracking and
event supervision, based on the inspected author descriptions. This is an
engineering inference, not a dataset selection. ROAD-Waymo offers similar
semantics at greater scale but has a gated acquisition route and restrictive
downstream terms. KITTI is a strong established tracking fallback. SVMOT is a
promising focused identity/occlusion candidate, rather than a replacement for
general road-event coverage simply because it is recent.

TUMTraf-A's project page reports 8,944 labeled frames; the linked 2025 paper
abstract reports 48,144 and additional 2D boxes. Neither figure is asserted as
the obtained release inventory. Reconcile the version and modality coverage
before implementing an adapter or promising a 2D evaluation protocol.

No candidate has passed all acceptance gates: authoritative terms suitable
for the intended use, working acquisition of actual media and identity
annotations, decoded media, parsed ground truth, and a frozen real subset.
TrafficMOT additionally needs explicit license terms. Research-use permission
must not be generalized into permission for a commercial product, hosted demo,
model redistribution, or unrestricted public media upload.

## Verified SVMOT metadata evidence

These are **metadata checks**, not dataset or model validation. Values were
computed from downloaded bytes and compared with the author's `SHA256SUMS`:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| train.txt | 314 | `45afa8d7e35e0940577ae1bcb5dc39aa0958336cf50113b312631a259f4b6a7a` |
| test.txt | 135 | `33d6c6aa614e58965bf1a7c705feea32f9b131a35f6bfd6247a36bb1a812ac81` |
| by_scene.json | 1270 | `6d4f00b86b534dcac1f074cc4656f4f12ecd14fac2f56a1f29bff3a3b371efeb` |

The author's scene mapping assigns scenes 01–04 to train and scenes 05–06
to test. Multiple sequences share each physical scene. No development
selection, validation split, or real-file manifest has been frozen.

The archive's **author-published**, not locally verified, SHA-256 is
`aae153a21a46f9fe37068ee006a65abd58894efaabc4390404eadcc08be8bd7a`.
The published MD5 is `0f8ef94e30e2b492411fadee8085ee10`. No partial or full
archive integrity result is claimed.

## Recheck procedure

Use the linked official routes; do not repair broken links with an unverified
mirror. Inspect an actual archive's terms and inventory before choosing it.
Record release identifier, exact URL, UTC retrieval time, archive/file hashes,
download and extracted sizes, and prerequisites. Access failures here do not
prove permanent removal. The next useful step is acquisition in a workspace
with reliable access, followed by the [preparation gates](data-preparation.md).
