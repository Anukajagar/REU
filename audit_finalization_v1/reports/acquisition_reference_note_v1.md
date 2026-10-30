# Acquisition reference — documented as UNKNOWN (v1 audit)

- The physical acquisition reference of the BIOPAC EEG recordings is **UNKNOWN**.
- It could not be recovered from any available source in this repository:
  - the v3 notebook contains no rereference call (searched: {'set_eeg_reference': 0, 'set_bipolar_reference': 0, 'average reference': 0, 'REST': 0, 'reref': 0, 'EcoG': 0}),
  - the `.acq` header exposes no reference attribute (checked `bioread` Datafile/channel attributes),
  - no acquisition-team documentation is present in `information\`.
- **No reference was applied or assumed by the audit.** The v3 pipeline also applied none
  (`set_eeg_reference` absent), so the saved files carry whatever reference the hardware used at
  recording time. This must be confirmed with the acquisition team before reference-sensitive
  features (e.g. Laplacian, current-source-density, or linked-mastoid derivations) are computed.

## Other assumed (not measured) metadata — recorded for transparency
- **Electrode positions**: the standard 10-20 montage was attached by the v3 pipeline
  (`set_montage(..., on_missing="ignore")`). No digitised positions exist in the dataset, so all
  topographic statements (ICA frontal weights, neighbour correlations) rest on this assumption.
- **EOG**: no dedicated EOG channel was recorded. The ocular detector uses the mean of
  Fp1/Fpz/Fp2 as a frontal proxy. This is an approximation, not a calibration.
