from import_assets import create_named_slices, _play

named_slices = create_named_slices()
slice = named_slices['taiko1']
_play(slice, 44100)
