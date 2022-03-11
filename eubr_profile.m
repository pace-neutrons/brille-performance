function eubr_profile()
do_profile = false;
if do_profile
    profile -memory on
end

lattice = [1., 1., 1., 90, 90, 90];
cut = d2d(lattice, [1 0 0 0], [-5,0.05,5], [0 1 0 0], [-5,0.05,5]);
n_repeats = 3;

fc_dir = 'force_constants';
fcs = {euphonic.ForceConstants.from_castep([fc_dir, filesep, 'quartz.castep_bin']), ...
       euphonic.ForceConstants.from_castep([fc_dir, filesep, 'La2Zr2O7.castep_bin']), ...
       euphonic.ForceConstants.from_castep([fc_dir, filesep, 'Nb-181818-s0.5-NCP19-vib-disp.castep_bin'])};
brille_npts = {10000, 5000, 20000};
dipole_params = {0.75, 1.0, 1.0};
materials = ["Quartz", "La2Zr2O7", "Nb"];
chunk = 50000;
filestr = sprintf("_%dqpts_%dchunk_%.0f", numel(cut.s), chunk, posixtime(datetime('now')));
tictoc_fname = ['out', filesep, char(sprintf("eubr_tictoc%s.txt", filestr))];
mprof_txt_fname = ['out', filesep, char(sprintf("eubr_mprof%s.txt", filestr))];
mprof_fname = ['out', filesep, char(sprintf("eubr_mprof%s", filestr))];
cohcry_args = {'conversion_mat', [1,0,0;0,1,0;0,0,-1], ...
               'chunk', chunk, ...
               'temperature', 5, ...
               'debye_waller_grid', [6, 6, 6], ...
               'bose', true, ...
               'negative_e', true};
n_threads = int32(30);
eu_interp_og_kwargs = {'n_threads', n_threads};
bri_interp_kwargs = {'useparallel', true ...
                     'threads', n_threads};
output_kwargs = {cohcry_args{:}, eu_interp_og_kwargs{:}, bri_interp_kwargs{:}, 'brille_npts', brille_npts{:}, 'dipole_parameters', dipole_params{:}};
writecell(output_kwargs, tictoc_fname);
fileid = fopen(tictoc_fname, 'a+');
for i = 1:length(materials)
    fprintf(fileid, "\n\nMaterial: %-15s qpts: %-10d chunk: %-10d\n", materials(i), numel(cut.s), chunk);
    eu_interp_kwargs = {eu_interp_og_kwargs{:}, 'dipole_parameter', dipole_params{i}};
    eu_cohcry = euphonic.CoherentCrystal(fcs{i}, cohcry_args{:}, eu_interp_kwargs{:});
    
    fprintf(fileid, "Euphonic (s)\n", numel(cut.s), materials(i));
    for j = 1:n_repeats
        tic;
        sim = disp2sqw_eval(cut, @eu_cohcry.horace_disp, [], 1.0);
        time = toc;
        fprintf(fileid,"%10.3f", time);
    end
    bri_args = {'interpolation_kwargs', struct(eu_interp_kwargs{:}), ...
                'n_grid_points', brille_npts{i}};
    fprintf(fileid, "\nBrille Init (s)\n", brille_npts{i}, materials(i));
    for j = 1:n_repeats
        tic;
        bri = euphonic.BrilleInterpolator.from_force_constants(fcs{i}, bri_args{:});
        time = toc;
        fprintf(fileid,"%10.3f", time);
    end

    bri_cohcry = euphonic.CoherentCrystal(bri, cohcry_args{:}, bri_interp_kwargs{:});
    fprintf(fileid, "\nBrille (s)\n", numel(cut.s), materials(i));
    for j = 1:n_repeats
        tic;
        sim = disp2sqw_eval(cut, @bri_cohcry.horace_disp, [], 1.0);
        time = toc;
        fprintf(fileid,"%10.3f", time);
    end
end
fclose(fileid);

if do_profile
    p = profile('info');
    dump_profile(p, mprof_txt_fname)
    profsave(p, mprof_fname);
    profile off
end
end

function dump_profile(prof, filename)
    extract = {'FunctionName' 'NumCalls' 'TotalTime' 'TotalMemAllocated' 'TotalMemFreed' 'PeakMem'};

    ft = prof.FunctionTable;

    maxTime = max([ft.TotalTime]);

    fn = fieldnames(ft);
    sd = setdiff(fn, extract);
    m = rmfield(ft, sd);

    percent = arrayfun(@(x) 100*x.TotalTime/maxTime, m, 'UniformOutput', false);
    [m.PercentageTime] = percent{:};
    sp_time = arrayfun(@(x) sum([x.Children.TotalTime]), ft);
    self_time = arrayfun(@(x,y) x-y, [ft.TotalTime]', sp_time, 'UniformOutput', false);
    [m.SelfTime] = self_time{:};
    percent = arrayfun(@(x) 100*x.SelfTime/maxTime, m, 'UniformOutput', false);
    [m.SelfPercentageTime] = percent{:};

    dataStr = evalc('struct2table(m)');

    % Remove HTML, braces and header
    dataStr = regexprep(dataStr, '<.*?>', '');
    dataStr = regexprep(dataStr, '[{}]', ' ');
    dataStr = dataStr(24:end);

    fh = fopen(filename, 'w');
    fwrite(fh, dataStr);
    fclose(fh);

end