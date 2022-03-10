lattice = [1., 1., 1., 90, 90, 90];
cut = d2d(lattice, [1 0 0 0], [-5,0.05,5], [0 1 0 0], [-5,0.05,5]);
n_repeats = 1;

fc_dir = 'force_constants';
fcs = {euphonic.ForceConstants.from_castep([fc_dir, filesep, 'quartz.castep_bin']), ...
       euphonic.ForceConstants.from_castep([fc_dir, filesep, 'La2Zr2O7.castep_bin'])};
brille_npts = {10000, 5000}
materials = ["Quartz", "La2Zr2O7"];
fname = ['out', filesep, char(sprintf("out_%.0f", posixtime(datetime('now'))))];
cohcry_args = {'conversion_mat', [1,0,0;0,1,0;0,0,-1], ...
               'chunk', 50000, ...
               'temperature', 5, ...
               'debye_waller_grid', [6, 6, 6], ...
               'bose', true, ...
               'negative_e', true};
n_threads = int32(30);
eu_interp_kwargs = {'dipole_parameter', 0.75, ...
                    'n_threads', n_threads};
bri_interp_kwargs = {'useparallel', true ...
                     'threads', n_threads};
bri_og_args = {};
output_kwargs = {cohcry_args{:}, eu_interp_kwargs{:}, bri_interp_kwargs{:}, bri_og_args{:}};
writecell(output_kwargs, fname);
bri_args = {bri_args{:}, 'interpolation_kwargs', struct(eu_interp_kwargs{:})};
fileid = fopen([fname '.txt'], 'a+');
for i = 1:length(fcs)
    eu_cohcry = euphonic.CoherentCrystal(fcs{i}, cohcry_args{:}, eu_interp_kwargs{:});
    
    fprintf(fileid, "Time to calculate %i q-points with Euphonic for %s:\n", numel(cut.s), materials(i));
    for j = 1:n_repeats
        tic;
        sim = disp2sqw_eval(cut, @eu_cohcry.horace_disp, [], 1.0);
        time = toc;
        fprintf(fileid,"%.3f s\n", time);
    end
    bri_args = {bri_og_args{:}, 'n_grid_points', brille_npts{i}};
    fprintf(fileid, "Time to initialise BrilleInterpolator for %i q-points for %s:\n", brille_npts{i}, materials(i));
    for j = 1:n_repeats
        tic;
        bri = euphonic.BrilleInterpolator.from_force_constants(fcs{i}, bri_args{:});
        time = toc;
        fprintf(fileid,"%.3f s\n", time);
    end

    bri_cohcry = euphonic.CoherentCrystal(bri, cohcry_args{:}, bri_interp_kwargs{:});
    fprintf(fileid, "Time to calculate %i q-points with Brille for %s:\n", numel(cut.s), materials(i));
    for j = 1:n_repeats
        tic;
        sim = disp2sqw_eval(cut, @bri_cohcry.horace_disp, [], 1.0);
        time = toc;
        fprintf(fileid,"%.3f s\n", time);
    end
end
fclose(fileid);