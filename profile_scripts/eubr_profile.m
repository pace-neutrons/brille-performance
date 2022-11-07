function eubr_profile()
do_profile = false;
if do_profile
    profile -memory on
end

py.importlib.import_module('utils');

lattice = [1., 1., 1., 90, 90, 90];
cut = d2d(lattice, [1 0 0 0], [-5,0.025,5], [0 1 0 0], [-5,0.025,5]);
%cut = d2d(lattice, [1 0 0 0], [-5,0.5,5], [0 1 0 0], [-5,0.5,5]);
n_repeats = 3;

fc_info = py.utils.get_fc_info();
brille_npts = [];
dipole_params = [];
fc_files = [];
for i = 1:length(fc_info)
    fc_files = [fc_files string(fc_info{i}{'filename'})];
    brille_npts = [brille_npts int32(fc_info{i}{'brille_npts'})];
    dipole_params = [dipole_params double(fc_info{i}{'dipole_parameter'})];
end

chunk = 0;
filestr = sprintf("_%dqpts_%dchunk_%.0f", numel(cut.s), chunk, posixtime(datetime('now')));
out_dir = py.utils.get_create_results_path(pyargs('lang', 'matlab'));
tictoc_file = sprintf("%s%seubr_tictoc%s.txt", out_dir, filesep, filestr);
mprof_txt_file = sprintf("%s%seubr_mprof%s.txt", out_dir, filesep, filestr);
mprof_file = sprintf("%s%seubr_mprof%s", out_dir, filesep, filestr);
cohcry_args = {'conversion_mat', [1,0,0;0,1,0;0,0,-1], ...
               'chunk', chunk, ...
               'temperature', 5, ...
               'debye_waller_grid', [6, 6, 6], ...
               'bose', true, ...
               'negative_e', true};
n_threads = int32(py.utils.NTHREADS);
eu_interp_og_kwargs = {'use_c', true, 'n_threads', n_threads};
bri_interp_kwargs = {'useparallel', true ...
                     'threads', n_threads};
output_kwargs = {cohcry_args{:}, eu_interp_og_kwargs{:}, bri_interp_kwargs{:}, 'brille_npts', brille_npts, 'dipole_parameters', dipole_params};
writecell(output_kwargs, tictoc_file);
fileid = fopen(tictoc_file, 'a+');
for i = 1:length(fc_files)
    fprintf(fileid, "\n\nMaterial: %-15s qpts: %-10d chunk: %-10d\n", fc_files(i), numel(cut.s), chunk);
    fc = euphonic.ForceConstants.from_castep(string(py.str(py.utils.get_fc_path(fc_files(i)))));
    eu_interp_kwargs = {eu_interp_og_kwargs{:}, 'dipole_parameter', dipole_params(i)};
    eu_cohcry = euphonic.CoherentCrystal(fc, cohcry_args{:}, eu_interp_kwargs{:});
    
    fprintf(fileid, "Euphonic (s)\n", numel(cut.s), fc_files(i));
    for j = 1:n_repeats
        tic;
        sim1 = disp2sqw_eval(cut, @eu_cohcry.horace_disp, [], 1.0);
        time = toc;
        fprintf(fileid,"%10.3f", time);
    end
    bri_args = {'interpolation_kwargs', struct(eu_interp_kwargs{:}), ...
                'grid_npts', brille_npts(i)};
    fprintf(fileid, "\nBrille Init (s)\n", brille_npts(i), fc_files(i));
    for j = 1:n_repeats
        tic;
        bri = euphonic.BrilleInterpolator.from_force_constants(fc, bri_args{:});
        time = toc;
        fprintf(fileid,"%10.3f", time);
    end

    bri_cohcry = euphonic.CoherentCrystal(bri, cohcry_args{:}, bri_interp_kwargs{:});
    fprintf(fileid, "\nBrille (s)\n", numel(cut.s), fc_files(i));
    for j = 1:n_repeats
        tic;
        sim2 = disp2sqw_eval(cut, @bri_cohcry.horace_disp, [], 1.0);
        time = toc;
        fprintf(fileid,"%10.3f", time);
    end
end
fclose(fileid);

if do_profile
    p = profile('info');
    dump_profile(p, mprof_txt_file)
    profsave(p, mprof_file);
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
