lattice = [1., 1., 1., 90, 90, 90]
cut = d2d(lattice, [1 0 0 0], [-5,0.1,5], [0 1 0 0], [-5,0.1,5]);
n_repeats = 3;

fc_dir = 'force_constants';
fcs = {euphonic.ForceConstants.from_castep([fc_dir, filesep, 'quartz.castep_bin']), ...
       euphonic.ForceConstants.from_castep([fc_dir, filesep, 'La2Zr2O7.castep_bin'])};
materials = ["Quartz", "La2Zr2O7"];
fname = ['out', filesep, char(sprintf("out_%.0f", posixtime(datetime('now'))))];
cohcry_args = {'conversion_mat', [1,0,0;0,1,0;0,0,-1], ...
               'chunk', 50000, ...
               'temperature', 5, ...
               'debye_waller_grid', [6, 6, 6], ...
               'bose', true, ...
               'negative_e', true};
eu_interp_kwargs = {'use_c', true, ...
                    'n_threads', int32(4), ...
                    'dipole_parameter', 0.75};
bri_interp_kwargs = {'useparallel', true, ...
                     'threads', int32(4)};
bri_args = {'n_grid_points', int32(2500)};
output_kwargs = {cohcry_args{:}, eu_interp_kwargs{:}, bri_interp_kwargs{:}, bri_args{:}};
writecell(output_kwargs, fname);
bri_args = {bri_args{:}, 'interpolation_kwargs', struct(eu_interp_kwargs{:})};
fileid = fopen([fname '.txt'], 'a+');
for i = 1:length(fcs)
    cohcry_args = {'conversion_mat', [1,0,0;0,1,0;0,0,-1], ...
                   'chunk', 50000, ...
                   'temperature', 5, ...
                   'debye_waller_grid', [6, 6, 6], ...
                   'bose', true, ...
                   'negative_e', true};
    eu_interp_kwargs = {'use_c', true, ...
                        'n_threads', int32(4), ...
                        'dipole_parameter', 0.75};
    bri_interp_kwargs = {'useparallel', true, ...
                         'threads', int32(4)};
    bri_args = {'n_grid_points', int32(2500), ...
                'interpolation_kwargs', struct(eu_interp_kwargs{:})};
            
            
    eu_cohry = euphonic.CoherentCrystal(fcs{i}, cohcry_args{:}, eu_interp_kwargs{:});
    
    fprintf(fileid, "Time to calculate %i q-points with Euphonic for %s:\n", numel(cut.s), materials(i));
    for j = 1:n_repeats
        tic;
        sim = disp2sqw_eval(cut, @euobj.horace_disp, [], 1.0);
        time = toc;
        fprintf(fileid,"%.3f s\n", time);
    end

    fprintf(fileid, "Time to initialise BrilleInterpolator for %i q-points for %s:\n", bri_args{2}, materials(i));
    for j = 1:n_repeats
        tic;
        bri = euphonic.BrilleInterpolator.from_force_constants(fcs{i}, bri_args{:});
        %disp2sqw_eval(cut, @euobj.horace_disp, [], 1.0);
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

% tic
% for i = ni:nf
%     wouts(i) = disp2sqw_eval(cuts(i), @euobj.horace_disp, pars, fwhh, '-all');
%     bri = euphonic.BrilleInterpolator.from_force_constants(fc, ...
%                                                            'n_grid_points', int32(2500), ...
%                                                            'interpolation_kwargs', struct('asr', 'reciprocal', ...
%                                                                                           'dipole_parameter', 0.75));
%     x = toc;
    %sprintf("Time to calculate %i q-points with Euphonic:", i);
end
fclose(fileid);
%cut = d2d(lattice, [1 0 0 0], [-5,0.1,5], [0 1 0 0], [-5,0.1,10], [0 0 0 1], [-5, 0.5, 100])

% horace_on
% cut_path='sqw/';
% %materials = ["quartz"];
% %cuts = struct("quartz", ["8meV_slice.d2d", "quartz_30L_qe.sqw", "quartz_h0L_qq.sqw"];
% 
% %cut_files = ["8.5meV_small", "vE_slice.d2d", "wE_slice.d2d"];
% %cut_files = ["quartz_h0l_qq.sqw", "quartz_9meV_qq.sqw", "quartz_30L_qe.sqw", "quartz_2ph_m4_0_qe.sqw"];
% %cut_files = ["quartz_30L_qe.sqw", "quartz_2ph_m4_0_qe.sqw"];
% %cut_files = ["quartz_9meV_qq.sqw"];
% cut_files = ["8.5meV_slice_new.d2d"];
% %cut_files = ["8.5meV_small.d2d"];
% %cut_files = ["0510_cut.d2d"]
% %cut_files = ["quartz_30L_qe.sqw"];
% ni=1;
% nf = length(cut_files);
% for i = ni:nf
%     cuts(i) = d2d(read_horace([cut_path, char(cut_files(i))]));
%     %cuts(i) = read_horace([cut_path, char(cut_files(i))]);
% end
% 
% fc = euphonic.ForceConstants.from_castep('quartz.castep_bin');
% euobj = euphonic.CoherentCrystal(fc, ...
%                              'asr', 'reciprocal', ...
%                              'reduce_qpts', true, ...
%                              'use_c', true, ...
%                              'n_threads', int32(4), ...
%                              'dipole_parameter', 0.75, ...
%                              'conversion_mat', [1,0,0;0,1,0;0,0,-1], ...
%                              'chunk', 50000, ...
%                              'temperature', 5, ...
%                              'debye_waller_grid', [6, 6, 6], ...
%                              'bose', true, ...
%                              'negative_e', true);
% fwhh = 1.0;
% pars = {100.0, 1.0};
% tic
% for i = ni:nf
%     wouts(i) = disp2sqw_eval(cuts(i), @euobj.horace_disp, pars, fwhh, '-all');
% end
% toc
% 
% bri = euphonic.BrilleInterpolator.from_force_constants(fc, ...
%                                   'n_grid_points', int32(2500), ...
%                                   'interpolation_kwargs', struct('asr', 'reciprocal', ...
%                                                                  'dipole_parameter', 0.75));
% 
% euobj_bri = euphonic.CoherentCrystal(bri, ...
%                              'chunk', 50000, ...
%                              'lim', 1e4, ...
%                              'conversion_mat', [1,0,0;0,1,0;0,0,-1], ...
%                              'temperature', 5, ...
%                              'debye_waller_grid', [6, 6, 6], ...
%                              'bose', true, ...
%                              'negative_e', true, ...
%                              'useparallel', true, ...
%                              'threads', int32(4));
% fwhh = 1.0;
% pars = {100.0, 1.0};
% tic
% for i = ni:nf
%     wouts_bri(i) = disp2sqw_eval(cuts(i), @euobj_bri.horace_disp, pars, fwhh, '-all');
% end
% toc
% 
% for i = ni:nf
%     keep_figure;
%     plot(cuts(i));
% end
% for i = ni:nf
%     keep_figure;
%     plot(wouts(i));
% end
% for i = ni:nf
%     keep_figure;
%     plot(wouts_bri(i));
% end
% 
% idx = 1;
% lims = [0.4, 0.6]
% cut1d = cut_dnd(cuts(idx), lims, []);
% wout1d = cut_dnd(wouts(idx), lims, []);
% wout1d_bri = cut_dnd(wouts_bri(idx), lims, []);
% 
% plot(cut1d);
% keep_figure;
% plot(wout1d);
% keep_figure;
% plot(wout1d_bri);