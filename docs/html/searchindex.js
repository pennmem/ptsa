Search.setIndex({docnames:["api/data","api/data/filters","api/data/readers","api/data/timeseriesx","api/extensions","api/index","changes","development","examples/classifier_time_series","examples/classifier_time_series_R1111M","examples/eeg","examples/eeg_full_session","examples/events","examples/events_SPC","examples/index","examples/pyFR_demo","examples/test_classifier_notebook-R1111M-presentation","examples/timeseriesx","filters","index","installation","ramdata","tutorial"],envversion:53,filenames:["api/data.rst","api/data/filters.rst","api/data/readers.rst","api/data/timeseriesx.rst","api/extensions.rst","api/index.rst","changes.rst","development.rst","examples/classifier_time_series.ipynb","examples/classifier_time_series_R1111M.ipynb","examples/eeg.ipynb","examples/eeg_full_session.ipynb","examples/events.ipynb","examples/events_SPC.ipynb","examples/index.rst","examples/pyFR_demo.ipynb","examples/test_classifier_notebook-R1111M-presentation.ipynb","examples/timeseriesx.ipynb","filters.rst","index.rst","installation.rst","ramdata.rst","tutorial.rst"],objects:{"ptsa.data.TimeSeriesX":{TimeSeriesX:[3,0,1,""]},"ptsa.data.TimeSeriesX.TimeSeriesX":{add_mirror_buffer:[3,1,1,""],append:[3,1,1,""],baseline_corrected:[3,1,1,""],create:[3,2,1,""],filtered:[3,1,1,""],from_hdf:[3,2,1,""],remove_buffer:[3,1,1,""],resampled:[3,1,1,""],to_hdf:[3,1,1,""]},"ptsa.data.filters":{ButterworthFilter:[1,0,1,""],MorletWaveletFilter:[1,0,1,""],MorletWaveletFilterCpp:[1,0,1,""],ResampleFilter:[1,0,1,""]},"ptsa.data.filters.ButterworthFilter":{filter:[1,1,1,""]},"ptsa.data.filters.MorletWaveletFilter":{filter:[1,1,1,""]},"ptsa.data.filters.ResampleFilter":{filter:[1,1,1,""]},"ptsa.data.readers":{BaseEventReader:[2,0,1,""],CMLEventReader:[2,0,1,""],EEGReader:[2,0,1,""],TalReader:[2,0,1,""]},"ptsa.data.readers.BaseEventReader":{as_dataframe:[2,1,1,""],find_data_dir_prefix:[2,1,1,""],modify_eeg_path:[2,1,1,""],normalize_paths:[2,1,1,""],read_matlab:[2,1,1,""]},"ptsa.data.readers.CMLEventReader":{modify_eeg_path:[2,1,1,""]},"ptsa.data.readers.EEGReader":{compute_read_offsets:[2,1,1,""],events:[2,3,1,""],read_events_data:[2,1,1,""],read_session_data:[2,1,1,""]},"ptsa.data.readers.TalReader":{get_bipolar_pairs:[2,1,1,""],get_monopolar_channels:[2,1,1,""]},"ptsa.emd":{calc_inst_info:[5,5,1,""],eemd:[5,5,1,""],emd:[5,5,1,""]},"ptsa.extensions":{circular_stat:[4,4,0,"-"],morlet:[4,4,0,"-"]},"ptsa.extensions.circular_stat":{circ_diff:[4,5,1,""],circ_diff_par:[4,5,1,""],circ_diff_time_bins:[4,5,1,""],circ_mean:[4,5,1,""],compute_f_stat:[4,5,1,""],compute_z_scores:[4,5,1,""],single_trial_ppc_all_features:[4,5,1,""]},"ptsa.filt":{buttfilt:[5,5,1,""],decimate:[5,5,1,""],firls:[5,5,1,""]},"ptsa.filtfilt":{filtfilt:[5,5,1,""],lfilter_zi:[5,5,1,""]},"ptsa.helper":{cart2pol:[5,5,1,""],centered:[5,5,1,""],deg2rad:[5,5,1,""],getargspec:[5,5,1,""],next_pow2:[5,5,1,""],pad_to_next_pow2:[5,5,1,""],pol2cart:[5,5,1,""],rad2deg:[5,5,1,""],reshape_from_2d:[5,5,1,""],reshape_to_2d:[5,5,1,""]},"ptsa.hilbert":{hilbert_pow:[5,5,1,""]},"ptsa.iwasobi":{IWASOBI:[5,0,1,""]},"ptsa.iwasobi.IWASOBI":{CRLB4:[5,1,1,""],ar2r:[5,1,1,""],armodel:[5,1,1,""],corr_est:[5,1,1,""],uwajd:[5,1,1,""],wajd:[5,1,1,""],weights:[5,1,1,""]},"ptsa.pca":{pca:[5,5,1,""]},"ptsa.wica":{WICA:[5,0,1,""],find_blinks:[5,5,1,""],remove_strong_artifacts:[5,5,1,""],wica_clean:[5,5,1,""]},ptsa:{emd:[5,4,0,"-"],filt:[5,4,0,"-"],filtfilt:[5,4,0,"-"],helper:[5,4,0,"-"],hilbert:[5,4,0,"-"],iwasobi:[5,4,0,"-"],pca:[5,4,0,"-"],wica:[5,4,0,"-"]}},objnames:{"0":["py","class","Python class"],"1":["py","method","Python method"],"2":["py","classmethod","Python class method"],"3":["py","attribute","Python attribute"],"4":["py","module","Python module"],"5":["py","function","Python function"]},objtypes:{"0":"py:class","1":"py:method","2":"py:classmethod","3":"py:attribute","4":"py:module","5":"py:function"},terms:{"001e":17,"002e":17,"0th":16,"0x101810160":17,"0x10d48aad0":16,"0x10d77be90":16,"0x10d91ba90":16,"0x10db48390":16,"0x111518610":8,"0x111535690":8,"0x1122a1590":16,"0x11360c610":16,"0x11381c610":16,"0x114009748":17,"0x1141b79b0":17,"0x114743310":16,"0x114fbac90":8,"0x11567d350":8,"0x11596a7d0":10,"0x1162587d0":10,"0x1162bfad0":10,"0x1167ecd10":10,"0x116b1cbd0":10,"0x11f300bd0":13,"0x11f85be90":13,"0x11f8da450":13,"0x11f9929d0":13,"0x11fa01090":13,"0x11fa01790":13,"0x11fa01e90":13,"0x11fa0d5d0":13,"0x11fa0dcd0":13,"0x11fa18410":13,"0x120416ad0":13,"0x120e541d0":13,"0x120ea32d0":13,"0x120ea39d0":13,"0x120eae110":13,"0x1213cc290":13,"1086182074789912e":5,"20th":16,"22nd":16,"2nd":5,"4b9f7b78e61d":15,"68l":11,"834190l":11,"boolean":[4,16],"break":12,"byte":[2,3],"case":[2,5,13,15,16,17,21],"class":[1,2,3,4,5,10,13,16,17,21,22],"default":[1,2,3,5,12,16,21],"final":[11,15],"float":[1,2,3,8,9],"function":[3,4,5,7,8,9,11,13,14,15,16,18,19,21,22],"import":[5,8,9,10,11,12,13,15,16,17,18,21,22],"int":[1,2,3,4,5,8,9,16,17],"long":[5,8,12],"new":[1,2,3,5,7,8,9,16,17,19,22],"null":3,"return":[1,2,3,4,5,8,9,10,13,15,16,17,21],"transient":5,"true":[2,5,8,9,10,15,16,21],"try":[2,5,12,15],"while":[16,21],APE:[12,15],AXE:12,For:[13,15,16,17,18,21,22],ICE:12,ICs:5,NOT:21,Not:3,OXE:12,One:2,That:12,The:[1,2,3,4,5,8,10,11,12,13,14,16,17,19,21,22],Then:5,There:10,These:10,Use:7,Will:10,With:[10,21],_____:21,__getitem__:15,__init__:3,_center:5,_event:[8,9],_filenam:2,_subplot:13,_tallocs_database_bipol:[8,9,11],a_z:16,abl:16,about:[5,10,12,16,21],abov:[15,16,21,22],abs:5,abs_join:11,abspath:11,acceler:4,access:[13,15,16,17,21],accomplish:11,account:2,accross:16,accru:13,acquisit:5,across:[10,16],action:[5,16,19],actual:[5,13,15,21,22],adapt:5,add:[3,5,10,22],add_mirror_buff:3,added:[2,3,16,21,22],adding:7,addit:[1,10,19],addition:11,adjac:10,advantag:13,after:[1,15,16,18,21,22],afterward:10,aggregate_valu:[10,13,21],aka:16,algorithm:[5,16],alia:[2,22],align:10,all:[2,3,5,7,10,12,15,16,18,19,21,22],all_ev:21,allow:[5,16,21],along:[5,16,22],alreadi:[7,16],also:[5,7,9,10,11,14,16,17,18,21,22],altern:[18,20],alwai:[13,21],amount:7,amplitud:5,analog:16,analys:[13,22],analysi:[5,16,21],angl:[4,5],angular:4,ani:[12,21],annot:22,anoth:[2,3,5,15,16,18,22],anova:4,ant:12,api:[19,22],append:[3,8,9,16,19],appli:[1,5,11,16],applic:16,appropri:[16,18],approxim:5,ar2r:5,ar_max:5,arang:[8,9,16,22],arbitrari:[3,16],arc:5,area:[16,21],arenterest:22,arg:[5,11],argument:[1,2,5,13,16,21,22],ark:12,arm:12,armodel:5,around:[3,10,17],arr:5,arrai:[1,2,3,4,5,9,10,12,13,15,16,17,18,19,21,22],array_lik:5,artifact:[5,10],artifici:5,as_datafram:2,ass:16,assert_array_equ:[9,16],assertionerror:3,assign:[16,22],associ:[10,12,15,21],assum:[5,10,22],assumpt:16,astyp:[8,9,16],attach:2,attempt:3,attr:[3,10],attribut:[10,13,15,16,17,21],auc:[8,9,16],auc_t_chop:8,auc_v_chop:8,author:5,auto:[8,9,16],automat:[2,17],autoregress:5,avail:[5,14,15,17,21],averag:[3,4,5,10],avgsurf:21,awkward:3,axes:[8,10,13,16],axessubplot:13,axi:[1,5,8,9,13,16,22],b_filter:[16,18],back:5,backward:5,bad:2,badg:12,bag:12,balanc:[8,16],ball:12,band:[5,12,18],bandwidth:16,bank:12,bar:13,barn:12,base64:3,base:[2,3,5,16],base_e_read:[8,9,15,16,21],base_eeg:[8,9,16,18,21],base_ev:[8,9,15,16,21],base_rang:3,baseeventread:[2,8,9,10,12,13,15,16],baselin:3,baseline_correct:3,baserawread:10,basic:[14,21,22],bat:12,bath:12,beach:12,beak:12,bean:12,bear:[12,16,21],becasus:11,becaus:[3,5,8,9,13,15,16,17,19,22],bed:12,bee:12,been:[2,5],befor:[5,7,13,16,18,22],begin:[3,8,9,10,22],behavior:[10,13,15],being:[8,9,16,22],bell:12,belong:[4,15,16],below:[5,12,14,16,18],bench:12,benchmark:16,besid:19,best:[5,21],better:5,between:[5,10,16,17,22],big:5,bin:4,binari:[2,3,10],bipoar:16,bipolar:[10,16,18,19,21],bipolar_eeg:10,bipolar_pair:[8,9,10,16,18,21],bird:12,bit:22,blind:5,block:5,blogspot:5,bloom:12,blush:12,board:12,boat:12,boi:12,bomb:[12,15],book:12,bool:[1,2,3,8],boot:12,both:[3,5,12,13],bowl:12,box:12,bp_eeg:[8,9,16,18],bp_eegs_filt:[16,18],bp_eegs_filtered_1:18,bp_pair:22,bpdistanc:21,bptalstruct:10,brain:[5,16],branch:[7,12],bread:12,brick:12,bridg:12,brodmann:21,broom:12,brush:[12,15],buffer:[2,3,10,16,21],buffer_offset:2,buffer_tim:[2,8,9,10,16,21],build:[16,19,21,22],built:[15,19,21],builtin:5,builtin_function_or_method:15,bunch:13,bush:12,butter:5,butterworth:[1,3,5,16,18],butterworthfil:16,butterworthfilt:[1,16],butterwoth:1,buttfilt:5,bw001:[10,12],bw001_24jul02_0001:[10,12],bw001_24jul02_0002:12,bw001_event:[10,12,13],bw001_tallocs_database_bipol:10,c_diff:4,cage:12,cake:12,calc_inst_info:5,calcul:[4,5,8,9,16],calf:12,call:[8,9,11,15,16,18,19,21,22],callabl:5,came:12,can:[2,3,5,8,9,10,12,13,15,16,17,20,21,22],cane:12,capabl:22,cape:12,car:12,card:12,carri:16,cart2pol:5,cart:12,cartesian:[5,16],cash:12,castellano:5,cat:12,categori:19,catfr:2,caus:[2,8],cave:12,cdiff_mean:4,center:[5,16],cerebrum:21,certain:10,ch0:[2,10,16],ch1:[2,10,16],chair:12,chalk:12,challeng:22,chang:[2,11,13],channel:[2,5,8,9,10,11,16,17,21],charact:10,cheatsheet:7,chebyshev:5,check:[16,19,21,22],cheek:12,chief:12,chin:12,choic:18,chop:[8,9],chop_time_seri:[8,9],chope:[8,9],chopped_time_seri:[8,9],chopper:[8,9],chunk:[2,5,9],circ_diff:4,circ_diff_par:4,circ_diff_time_bin:4,circ_mean:4,circular:4,circular_stat:5,clai:12,class_weight:[8,9,16],classifi:[9,14,16,19],classifier_arrai:8,classifier_array_chop:8,classifier_array_long:8,classifier_array_non_chop:8,classifier_data:[8,9],classifier_data_:9,classifier_time_seri:8,classifier_time_series_:8,classifierdata:[8,9],classmethod:3,clean:[5,22],cliff:12,clock:12,clone:20,cloth:12,cloud:12,clown:12,cml:[10,12,21],cmleventread:[2,10],cmlreader:21,coat:12,code:[2,5,7,9,11,15,16,19,21,22],coeefici:16,coef_:16,coeffici:[5,16],coin:12,collaps:21,collect:[8,9,16],color:16,column:[2,5,12,13,15,21],columnwis:5,com:[5,20],combin:[5,16],come:22,command:[7,22],commit:7,common:[2,8,9,16,22],common_root:[2,10,13],comp:5,companion:5,compar:[4,16],comparison:17,compat:7,compil:[8,16,19],complet:22,complex:[4,13],complic:3,compon:[5,10,16,18],compos:5,composit:12,comput:[1,4,5,8,9,18,19,21,22],compute_classifi:[8,9],compute_classifier_featur:9,compute_classifier_flag:[8,9],compute_continuous_wavelet:[8,9],compute_event_wavelets_from_session_wavelet:8,compute_f_stat:4,compute_features_recalls_normalization_param:8,compute_features_using_zscoring_param:[8,9],compute_probs_t:[8,9],compute_read_offset:2,compute_wavelet:[8,9],compute_z_scor:4,compute_zscored_featur:8,compute_zscoring_param:[8,9],concat:[8,22],concaten:[3,8,10,13,21],condit:[5,17],cone:12,configur:21,consecut:22,consider:10,constant:5,construct:[1,2,10,16,17,21],constructor:[3,16,21,22],consult:22,contact:21,contain:[1,2,3,5,8,9,10,15,16,18,19,21,22],contamin:[10,16],conten:15,content:[15,16,19,22],contingu:5,continu:[8,9,16],conveni:[10,13,17,18,19,21,22],convert:[2,5,16,21],convolut:16,cooefici:9,coord:[3,10,17,22],coordin:[3,5,10,16,17,22],copi:2,cord:[12,21],core:[2,11,13,16,17],corn:12,corr_est:5,correcpond:8,correct:[3,5],correspond:[5,9,10,16],correspong:2,couch:12,could:[8,10,15,16,21],cound:16,covari:5,cow:12,cpickl:[8,9],cpu:1,crane:12,creat:[3,5,10,15,16,17,18,20,21,22],crit:5,criteria:15,criterion:5,crlb4:5,crlb:5,crow:[12,15],crown:12,crteat:18,cthr:5,cube:[12,15],cup:12,current:[2,19],current_process:10,curv:16,custom:19,cut:9,cutoff:5,cylindr:5,dad:12,darpa:21,dart:12,dat:5,dat_t:5,data1:[2,21,22],data2:[2,21],data:[1,2,3,5,7,8,9,11,12,13,14,15,16,18,19,22],dataarrai:[3,10,17,18,19,22],databas:2,datachopp:[8,9],datafil:2,datafram:[2,12,13],dataroot:[2,8,9],dataset:[5,16],datatyp:12,dd2:5,ddof:[8,9,16],deal:[3,12],dec:12,decai:16,decim:5,decompos:18,decomposit:[1,4,5],deer:12,def:[8,9,17],defin:[11,18,19],definit:10,deg2rad:5,degre:5,demix:5,demo:14,demonstr:[11,16],denois:5,denomin:5,denot:[12,16],depend:[3,17,19],deprec:[8,16],deprecationwarn:[8,16],describ:[1,5,8,21],desir:[3,5,22],desk:12,detail:3,determin:[2,5,8,9,16,21],dev:[8,9],develop:19,diagon:5,dict:[3,17],dictionari:3,did:[10,22],differ:[2,4,10,12,13,16,17,18],differennt:16,diffrent:19,dim:[3,8,17,22],dimarrai:19,dime:12,dimenns:16,dimens:[2,3,4,5,10,11,16,22],dimension:[5,10,16],dimmension:22,dir:2,dir_prefix:2,direct:5,directli:[7,17],directori:[2,10,15,16,21],dirref:16,discard:16,discuss:21,disk:[3,8,9],dispali:5,displai:15,dissip:5,distribut:5,ditch:12,divid:[4,5,16],doc:17,dock:12,document:[3,22],doe:[5,12,16,20],doesn:13,dog:12,doll:12,don:[7,13],done:17,door:[12,21],dot:16,down:12,downsampl:[1,5,17],dress:12,drift:5,drive:[8,9,16],drop:[2,5],drum:12,dshape:5,dtype:[8,10,12,13,15,16,17,21,22],dual:16,duck:[12,15],due:10,dump:[8,9],durat:[3,8,9,16],dure:[15,16],e_path:[8,9,16,21],each:[2,3,4,5,10,12,15,16,21],ear:12,easi:22,easier:[5,22],easili:11,ecog:10,edf:[8,16],edg:[5,16],edgecolor:16,eeg:[2,5,8,9,11,12,13,14,15,16,18,22],eeg_fname_replace_pattern:[2,21],eeg_fname_search_patt:2,eeg_fname_search_pattern:[2,21],eeg_read:[8,9,11,16,21],eegeffset:2,eegfil:[2,8,9,10,12,15,16,21],eegoffset:[8,10,12,15,16,21],eegread:[2,8,9,10,11,15,16],eel:12,eemd:5,effect:[5,16],effici:21,egg:12,eigenvalu:5,eigratio:5,either:[1,16,17],electrod:[5,9,10,16,18,19],element:[5,16,22],elf:12,elimin:[3,10,21],eliminate_events_with_no_eeg:[2,8,9,15,16,21],eliminate_nan:2,els:8,emd:5,empir:5,empric:5,empti:[2,4,17],enam:21,encod:[3,16],end:[2,3,5,10,16,22],end_offset:2,end_tim:[2,8,9,10,16,21],enhanc:5,enough:[5,13],ensembl:5,ensur:[16,21],entir:[2,5,8,9,11,15,16],entri:[2,3,21,22],env:[8,10,16],environ:20,eog:5,eog_elec:5,ephi:10,epoch:[8,9,12,16],eps0:5,equal:16,equat:16,equival:[5,15],error:16,essenc:16,essenti:16,estim:[5,16],etc:[2,15,16,19,21],etyp:21,ev_path:15,even:[5,21],event:[2,8,9,12,13,14,15,16,18],event_path:21,events_all_ltp093:[10,13],everi:2,evs:[8,9,16],evs_sel:[9,16],evs_val:16,exact:5,exactli:[16,21],examin:[15,16],exampl:[2,5,10,13,15,16,17,18,19,21,22],except:[1,5],execut:[8,9],exercis:22,exist:7,exp_vers:10,expect:[5,16,22],experi:[10,12,13,15,20,21],experiment:21,explanatori:12,explicitli:[2,17],explor:[12,22],expon:16,express:[2,5,16,22],expvers:[16,21],exract:2,extend:5,extens:5,extra:[2,12,16,21],extract:21,eyeblink:5,f_stat:4,face:12,facecolor:16,facilit:[16,19,21],fact:[9,16,18,21],factor:5,factori:3,fail:3,fairli:5,fals:[1,2,3,5,8,9,10,16,21],familiar:22,fan:12,farm:12,fast:5,fast_rat:5,faster:5,fastpath:3,favor:[8,16],featur:[8,9,16,19],features_list:8,fenc:12,few:[5,10,22],fid:[8,9],field:[2,10,12,13,15,16,21],fig:[16,17],figsiz:16,figur:16,file:[2,3,8,10,11,13,15,16,17,19,20,21],filenam:[2,3,8,9,10,11,12,13,15,16,21],filesystem:15,fill:[4,13],film:12,filt:5,filt_typ:[3,5,16,18],filter:[0,3,8,9,10,15,16,19],filtfilt:5,find:[5,8,10,16,22],find_blink:5,find_data_dir_prefix:2,find_dir_prefix:2,fir:5,firl:5,first:[4,5,8,9,10,11,12,15,16,18,21,22],first_bp:16,first_bp_manu:16,fish:12,fit:[8,9,16],fit_intercept:16,fix:[10,22],fixm:3,flag:[1,2,8,9,12,15],flair:12,flame:12,flea:12,float64:[5,10,16,17],floor:12,fluctuat:5,flute:12,foam:12,fog:12,folder:[2,11,15],follow:[2,5,8,9,10,15,16,17,19,21,22],food:12,foot:12,fork:12,form:[5,16,18],format:[3,10,16,17,19,21],formula:16,fort:12,forward:5,found:[5,10,17],four:5,fox:12,fpr:16,fpr_in:16,fpr_out:16,fr1:[10,14,16,21],frame:13,framework:21,freq:[1,8,9,16],freq_rang:[1,3,5,16,18],freqnenc:16,frequenc:[1,3,5,8,9,16,17,18],frequency_dim_po:[1,8,9],fresh:20,frog:12,from:[1,2,3,5,8,9,11,12,13,14,15,16,17,18,21,22],from_hdf:[3,17],from_record:13,fruit:12,fstat:4,ftype:5,fudg:12,full:[3,11,22],full_session_eeg:11,funuct:15,fur:12,further:19,futur:7,gain:[5,10,16],gate:12,gaussian:5,gees:[12,15],gener:[5,17,21],get:[2,5,10,11,15,16,17,18,21,22],get_bipolar_pair:[2,8,9,10,16,21],get_bp_data:[8,9],get_ev:[8,9],get_monopolar_and_bipolar_electrod:[8,9],get_monopolar_channel:[2,8,9,10,11,16,21],get_valu:10,getargspec:5,girl:[12,15],git:20,github:20,give:[10,12,16],given:[1,2,5,16,22],glass:12,glove:12,glue:22,gnu:5,goat:12,gold:12,good:[5,16,19,22],grai:21,grape:12,grass:12,greater:5,group:13,groupbi:13,grpname:21,guarante:5,guard:12,guess:16,guidelin:19,gyru:21,h5netcdf:20,h5py:3,had:5,ham:5,hand:[8,12,16,21],handi:22,handl:[3,16],happen:15,hard:[8,9,16],has:[2,5,8,9,10,12,15,16,17,19,21,22],hat:12,have:[2,5,10,12,13,15,16,17,18,19,21,22],hawk:12,hdf5:3,heart:12,heavili:[5,10],height:5,help:10,hen:12,henc:19,here:[5,8,9,11,12,14,15,16,18,21,22],heurist:[8,16],high:[5,16],higher:[4,17],highli:22,hilbert:5,hilbert_pow:5,hill:[12,15],hole:12,hoof:[12,15],hook:[12,15],horn:12,hors:[12,15],hose:12,hous:[12,15],how:[2,11,12,16,21,22],howev:[5,10,15,16,21],hstack:[8,9],hte:[2,16],html:5,http:[5,20],hyperplan:16,ica:5,icaeeg:5,idea:[16,22],ident:22,identifi:5,ignor:3,iir:5,implement:[2,5],impli:[5,16],implicit:22,includ:[2,7,15,22],inclus:3,increas:16,inde:16,independ:5,index:[1,13,16,17,18,21,22],indexread:[10,13],indic:[1,2,4,12,21],indici:5,individu:[2,16,21],indivsurf:21,infomax:5,inform:[5,9,10,11,12,16],infrom:21,initi:[5,8,16,18,21],initial_offset:[8,9],ink:12,inlin:[8,9,10,13,16,17],input:[1,2,5,8,9,15,16,18,19],insid:[5,18],inspect:5,instal:[16,19],instanc:[3,17,18,21],instantan:5,instead:[5,7,9,17],instruct:[16,21],int16:[10,16],int64:[17,22],integ:[2,5,16,22],interact:[17,19],intercept:16,intercept_:16,intercept_sc:16,interest:[10,16,22],interestingli:22,interfac:[4,10,13],intern:[3,17,21],interv:[8,21],introduct:[19,22],intrus:[10,12,15,16,21],invers:5,involv:[3,7],ipython:[15,16],is_stim:10,isn:13,isr:5,isstim:[16,21],issu:[2,22],item:[10,12,15,16,21],item_nam:10,item_num:10,itemno:[10,12,15,16,21],iter:5,its:[15,16,17,18,22],iwasobi:5,jail:12,jakub:5,jar:12,jeep:12,jet:12,job:18,join:[8,9,11],joint:5,json:[10,13,21],jsonindexread:[10,13],judg:[12,15],juic:[10,12],jupyt:14,just:[3,9],kbyanc:5,keep:[12,16,19],kei:12,kept:21,keyword:[1,2,21],khz:3,king:12,kite:12,know:[2,13,15,22],kthr:5,kwd:[1,2],lab:[10,21],label:[2,3,8,10,12,16,22],lake:12,lamb:12,lambda:11,lamp:12,land:12,larg:[7,8,9],last:[5,8,9,15],later:22,launch:1,law:16,lawn:12,lead:3,leaf:12,learn:[17,19,22],least:[3,5],leav:22,left:21,leg:12,legaci:[3,7,19],len:[4,5,16,17],length:[2,3,4,5],leond:10,less:[5,8,9,17],let:[10,11,12,15,16,17,18,21,22],letter:19,level:[4,11],levinson:5,lfilter:5,lfilter_zi:5,lib:[8,10,16],liblinear:[8,9,16],librari:[8,16,20],lie:16,like:[1,3,10,13,17,19,21],linalg:5,line2d:[8,10,16,17],line:[7,8,10,16,17],linear:5,linear_model:[8,9,16],linspac:[5,16,17],lip:12,list:[1,5,10,11,12,13,15,16,21,22],liter:10,littl:22,live:13,load:[3,8,9,10,16,21],lobe:21,loc1:21,loc2:21,loc3:21,loc4:21,loc5:21,loc6:21,loc:13,local:[12,15],locat:[8,9,10,11,12,13,15,16,21],lock:12,loctag:21,log10:[8,9,16],log_pow_wavelet:[8,9],log_session_wavelet:8,logarithm:16,logaritm:16,logist:16,logisticregress:[8,9,16],logspac:[8,9,16],loo:16,look:[10,12,16,19,21,22],loop:[8,16],loop_axi:3,loot:12,lot:[5,12],low:[4,16],lowpass:5,lpog10:[21,22],lpog11:21,lpog12:21,lpog13:21,lpog14:21,lpog1:21,lpog2:[21,22],lpog3:21,lpog4:21,lpog5:21,lpog6:21,lpog7:21,lpog9:[21,22],lpog:21,lr_classifi:[8,9,16],lsag:21,ltp:[10,13],ltpfr2:14,m2b:[8,9,16,18],m_k:5,machin:[12,19],made:16,magnitud:[4,5],mai:[5,9,16,18,20],mail:12,main:[10,19],makarov:5,make:[5,7,17,18,19,22],mani:16,manipul:21,manual:16,map:12,mapper:16,mark:[7,10,12],mask:16,master:[7,22],mat:[2,8,9,10,11,12,13,15,16,21],match:[15,16,21],matlab:[2,5,16,21],matplotlib:[8,9,10,13,16,17],matric:5,matrix:[4,5],matter:[18,21],max:[5,13],max_freq:1,max_it:16,max_mod:5,maximum:5,maxnumit:5,maze:12,mean:[2,8,9,10,12,13,16],mean_powers_nd:[8,9,16],mean_powers_r:[8,9,16],mean_tsm:22,measur:16,memori:[8,9,10,16,19,21],merg:7,metadata:3,method:[2,5,10,17,21],metric:[8,9,16],middl:21,might:[2,8,9,10],milk:12,millisecond:[3,12],min:13,min_freq:1,min_tsm:22,miniconda2:10,miniconda:[8,16],minimum:[5,17,22],mirror:3,mode:[3,5,9],moder:5,modern:7,modifi:7,modify_eeg_path:2,modul:[5,8,15,16,17,19,21,22],mole:12,mono:21,monopoartobipolarfilt:16,monopolar:[2,16,18,21],monopolar_channel:[8,9,16,21],monopolartobipolarfilt:16,monopolartobipolarmapp:[8,9,10,16],montag:[10,21],moon:12,moos:12,more:[5,9,10,13],moreletwaveletfilt:16,morlet:[1,5,8],morletwaveletfilt:[1,8,9,16],morletwaveletfiltercpp:[1,4,8],morletwaveltfilt:16,most:[15,19,21,22],moth:12,mount:[2,12,15,21],mous:12,mouth:12,movement:10,msoffset:[10,12,15,16,21],mstat:[8,9,16],mstime:[10,12,15,16,21],much:[5,13,21,22],mud:12,mug:12,mule:12,multi:[3,10],multi_class:16,multichannel:17,multidimension:3,multipl:17,multiplay:5,muscl:10,must:[2,3,4,5,7,17],n_bp:4,n_channel:17,n_freq:4,n_job:16,n_perm:4,n_thread:4,nail:12,name:[2,3,5,8,11,12,13,15,16,17,19,21,22],namedtupl:[8,9],nan:[2,16,21],nanmean:[8,9],nbc:5,nchanel:5,ncomp:5,ndarrai:[1,2,5],necessari:[5,16,17],need:[3,11,12,15,16,17,19,21,22],nest:[5,12],net:12,netcdf4:20,netcdf:19,neural:5,neurosci:5,new_classifier_data_:8,new_rat:17,newsiz:5,next:[5,10,11,21],next_pow2:5,nice:[13,16],no_reref:21,nobserv:5,nois:10,noise_std:5,noisi:17,noisy_sinusoid:17,non:[2,5,16],non_chop:8,none:[1,2,3,4,5,16],nonreref:2,noreref:[2,10,11,12,15,16,21],normal:[5,16,17,21],normalize_eeg_path:[2,21],normalize_path:2,nose:12,note:[2,3,5,9,10,11,12,22],notebook:[10,14,16],notic:[15,16,18,22],now:[3,5,16,17,21,22],npt:[8,9],num_ensembl:5,num_mp_proc:[3,5],num_point:17,num_sift:5,number:[1,2,4,5,8,9,10,12,15,16,17,21],number_of_compute_iter:[8,9],number_of_samples_in_resolut:[8,9],numer:5,numpi:[2,3,5,8,9,10,11,12,13,15,16,17,19,20,21,22],nyquist:5,oak:12,oar:[12,21],obj:5,object:[1,2,3,5,10,12,13,15,16,17,18,19,21],observ:4,obtain:[16,21],obvious:22,occurr:2,ocnstruct:15,octav:5,ocular:5,odd:5,offset:[2,9,16,21],often:[17,22],old:19,older:19,ommit:21,onbject:16,onc:[5,8,9,10,15,16,18],one:[3,5,10,15,16,18,20,21,22],ones:[2,5,7],onli:[5,8,9,10,15,16,17,19,21,22],onset:21,onth:16,open:[2,8,9,19],oper:[8,9,15,16,18,19],opt:5,option:[1,5,7,15,16],order:[1,2,3,5,16,18,21,22],ordereddict:[8,10],organ:[13,21],orient:12,origin:[1,2,3,17],other:[3,10,12,16],other_resampl:17,our:[10,15,16,21,22],ourselv:10,out:[1,8,9,10,11,12,13,15,16,17,18,21,22],output:[1,5,8,9,15,16,18,19,21,22],outsample_featur:4,over:[1,4,10],overrid:3,ovr:16,owl:12,own:[3,13],packag:[8,10,16,17,18,19,22],pad:5,pad_to_next_pow2:5,pad_to_pow2:[3,5],padlen:5,padtyp:5,page:14,pail:12,pair:[10,16,18,21],pairs_path:10,pairwis:18,palm:12,panda:[12,13,17],pant:12,parallel:[1,4],param:[2,9,10],paramet:[1,2,3,4,5,10,13,16,18,21],paramsread:10,park:12,part:[12,22],partial:2,partit:4,pass:[3,5,10,16,17,18,21],past:12,path:[2,3,8,9,10,11,15,16],pathcollect:16,patient:16,pattern:2,pca:5,pea:12,peach:12,pear:12,pearl:12,pedestrian:9,pen:12,penalti:[8,9,16],pennmem:20,per:[3,5],perform:[4,8,9,10,15,16],period:10,persist:10,pet:12,petkov:5,petr:5,phase:[1,4,5,16,17],phase_diff:4,phase_wavelet:[8,9,16],phase_wavelet_sess:[8,9],phone:12,pick:[5,16],pie:12,pig:12,pin:12,pipe:12,pipelin:[8,9],pit:[12,15],pkl:[8,9],place:[2,12,16],plain:22,plane:[12,16],plant:12,plate:[12,15],pleas:[8,16,22],plot:[8,9,10,12,13,16,17],plt:[8,9,10,13,16,17],png:8,point:[2,3,5,8,9,10,11,16,17,21],pol2cart:5,polar:5,pole:12,pond:12,pool:[1,12],popul:21,port:5,portion:5,posit:[1,9,12,13,15,16],possibl:[5,16,19],post:5,potenti:16,pow_wavelet:[8,9,16],pow_wavelet_chop:[8,9],pow_wavelet_list:8,pow_wavelet_sess:[8,9],power:[1,5,8,9,16],ppc_output:4,pre:15,prec_by_serialpo:13,prec_seri:13,predecessor:22,predict_proba:[8,9,16],prefer:18,prefix:2,prepare_classifier_data:9,prepend:15,present:[2,3,7],pretti:12,prevent:3,previou:21,princ:12,princip:5,principl:[8,9],print:[1,8,9,10,13,15,16,17,21,22],printout:22,prob:[8,9],probabl:[8,9,16],problem:16,probs_arrai:[8,9],probs_list:[8,9],procedur:21,proceed:22,process:[3,5,7,16,21],product:[9,16],project:[16,21],proper:1,properti:21,protocol:[10,13,21],provid:[4,5,10,11,17,19,21,22],ptsa:[1,2,3,5,7,8,9,10,11,12,13,14,15,16,17,18,20,21],ptsa_new:20,ptsa_new_git:[8,9,16],pull:7,pure:[5,13],pure_rang:5,purpos:[10,11,16],purs:12,push:5,pyfr:[12,14],pyplot:[8,9,10,13,16,17],pytest:7,python2:[8,10,16],python:[5,7,12,16,17,20,21,22],pywavelet:[19,20],quarter:22,queen:12,queri:[13,21],question:17,quick:17,quickli:4,quit:22,r1060m:11,r1060m_12aug15_1425:11,r1060m_event:2,r1111m:[8,9,10,13,16,21],r1111m_event:[16,21],r1111m_fr1_0_22jan16_1638:[16,21],r1111m_fr1_2_26jan16_1408:10,r1111m_fr1_3_02feb16_1528:21,r1111m_tallocs_database_bipol:[16,21],r_est:5,rad2deg:5,radian:5,radii:5,radiu:5,rahter:12,rain:12,rais:3,rake:12,ram:[8,14,19],ram_fr1:[2,8,9,16,21],random:17,random_st:16,rang:[1,3,5,10,13,17,18],rapidli:13,rare:17,rat:12,rate:[1,2,3,5,16,17],rather:[10,13],ratio:5,raw:[13,16],rawbinwrapp:2,reach:5,read:[2,8,9,11,12,13,14,15,16,19,20,22],read_events_data:2,read_matlab:2,read_session_data:2,reader:[0,5,8,9,10,11,12,13,15,16,17,19,21],readi:[16,21],real:16,realiz:5,reall:16,realli:[10,22],rearrang:22,reason:[3,16],rec:[12,15,16,21],rec_start:12,rec_word:12,recal:[4,8,9,10,12,13,15,16,21],recall_prob_arrai:[8,9,16],recalled_ind:16,recalls_arrai:16,recalls_list:8,recarrai:[2,3,10,12,13,15,16,21],recent:15,recommend:[20,22],record:[2,10,12,13,15,16,21],recov:5,rectim:[10,12,15,16,21],refactor:16,refer:[15,16,19,21,22],referenc:10,refresh:22,regiular:11,regress:16,rel:[5,10,16,21],relat:19,reli:[19,22],remain:16,remaind:13,rememb:22,remot:15,remov:[2,3,5,8,10,16,18,21],remove_bad_ev:2,remove_buff:[3,8,9,10,16],remove_strong_artifact:5,renam:[8,9],reorder:16,repalc:2,replac:[2,10,21,22],report:16,repositori:20,repres:[2,12,16,19],represent:5,request:[3,7,16],requir:[3,7,22],reref:[2,21],rereferenc:10,resampl:[1,3],resampled_r:3,resamplefilt:1,resampler:1,reserv:12,reset:3,reshap:[5,8,9,16,22],reshape_from_2d:5,reshape_to_2d:5,resolut:[8,9,17],resolv:16,respons:5,result:[4,5,18,22],retain:9,retriev:10,reus:1,rewrit:16,rhino:[2,10,11,12,15],rhino_root:[10,11,12,13,15,21],rib:12,rice:12,rich:17,rid:11,rlevinson:5,rmax:5,road:12,roc:16,roc_auc_scor:[8,9,16],roc_curv:[8,9,16],roc_curve_data_in:16,roc_curve_data_out:16,rock:[12,15],roof:12,room:12,root:[2,12],rope:12,rose:12,roughli:5,round:[1,8,9],round_to_original_timepoint:1,rrel:16,rudimentari:16,rug:12,rule:5,run:[5,7,8,9,15,16,18,19],runc:9,rune:[8,9],runner:7,runtimewarn:10,s256:[10,12,15,16,21],s32:22,sai:16,sail:12,salt:12,same:[1,4,5,13,17,21],sampl:[1,2,3,5,12,16,17],sample_r:[5,17],sampler:[3,5,8,9,10,16,17],save:[3,8,9,13],savefig:8,scalar:[2,5,17],scale:5,scalp:[10,13],scalp_ev:2,scatter:16,scheme:2,school:12,schur:5,scientif:22,scipi:[5,8,9,16,19,20,22],score:[8,9,16],screen:[15,21,22],script:22,sea:12,seal:12,search:2,seat:12,second:[2,3,4,5,8,9,10,11,16,21,22],second_bp:16,second_bp_manu:16,section:21,see:[3,5,12,15,16,19,21,22],seed:12,seem:10,segment:[8,16,21],sel:[10,17],select:[16,17,21,22],selector:16,self:[2,12,19],sens:16,sentinel:21,separ:[5,7,8,9,16],seri:[1,2,3,9,13,14,16,17,22],serial:[13,15],serialpo:[10,12,13,15,16,21],serialposit:13,seriec:16,sess_end:12,sess_max:[9,16],sess_min:[9,16],sess_start:[10,12],session:[2,8,9,10,11,12,15,16,21],session_bp_eeg:[8,9],session_data:[8,9],session_dataroot:[2,8,9,11],session_eeg:[8,9],session_list:8,session_mask:[8,9],session_num:8,session_read:[8,9],session_wavelet:8,session_wavelet_chop:8,session_zscore_mean_pow:8,sessions_ev:8,sessions_mask:8,set:[1,2,5,8,9,10,16,17,18,21],setup:[8,16,20],sever:19,shape:[5,8,9,11,16,22],shark:12,sheep:12,sheet:12,shell:12,shield:12,shift:5,ship:12,shirt:12,shoe:12,shorten:16,should:[1,2,3,4,5,10,16,17,22],show:[16,18],shown:5,shrimp:12,sigmi:5,sign:12,signal:[2,5,10,16,17,18,19,21,22],signaltool:5,significantli:19,similar:17,similarli:5,simpl:[9,13,16,17,18],simpli:[15,16,22],simplifi:[16,19],sin:[5,17],sinc:[8,9,12,15,16,21,22],sine:[5,17],singl:[16,17,21,22],single_session_ev:8,single_trial_ppc_all_featur:4,sink:12,sinuosoid:17,site:[8,10,16],size:[5,11],ski:12,skip:[5,16],skipna:16,sklearn:[8,9,16],skunk:12,sky:12,sleev:12,slice:[5,8,15],slice_s:[8,9],slime:12,slow:[5,7],slow_rat:5,slush:12,small:13,smaller:[8,9],smile:12,smoke:12,smooth:19,snail:12,snake:12,snow:12,soap:12,sock:12,solet:16,solv:5,solver:[8,9,16],some:[3,7,10,12,15,17,21,22],someth:18,sometim:16,sort:[21,22],soup:12,sourc:[5,19],space:[5,16],spacedbetween:16,spark:12,spear:12,specif:[5,10,16,19],specifi:[2,3,5,9,15,16,17,18,21,22],spectra:1,spectral:16,spectrum:16,speed:10,split:11,spong:12,spoon:12,spring:12,squar:[5,12],squeez:[11,16],stair:12,stand:21,star:[10,12],start:[2,3,5,11,16,17,18,21],start_offset:[2,8,9],start_tim:[2,8,9,10,16,21],start_time_posit:16,stat:[8,9,16,22],state:5,statist:[12,19,22],statrt:16,std:[8,9],std_fact:5,std_tsm:22,steadi:5,steak:12,steam:12,stem:[12,15],step:[3,5,16],stick:12,still:[5,8,19],stim_list:10,stim_param:[2,10],stimamp:[16,21],stimanod:[16,21],stimanodetag:21,stimcathod:[16,21],stimcathodetag:21,stimlist:[16,21],stimloc:[16,21],stone:12,stool:12,stop:[3,16,18,21],store:[2,4,5,8,9,10,11,12,15,16,17,21,22],storm:12,stove:12,str:[1,2,3,5],stragn:16,strain:[8,9],straw:12,street:12,string:[10,12],struct:[2,16],struct_typ:21,structur:[2,13,21],style:[8,9],subclass:[3,10,19,22],subject:[8,9,10,11,12,13,15,16,21],submit:7,subplot:17,subsequ:[8,9,16,21],subtract:[2,3,16],suce:16,suffix:10,suit:12,sum:[5,16],summari:15,sun:12,supporess:16,support:[5,8,16,19],suppress:5,sure:[5,19],swamp:12,swapaxes_tsm:22,swig:20,sword:12,symmetri:5,syntax:[15,18,21,22],sys:[8,9,15,16],system:[10,15,16],sytax:13,tabl:12,tagnam:21,tail:12,tak:[8,9,16],take:[8,10,12,15,16,17,18,19,22],tal:[2,8,9,10,11,16,21],tal_fil:11,tal_path:[8,9,16,21],tal_read:[8,9,10,11,16,21],tal_struct:21,talread:[2,8,9,10,11,15,16],tank:[12,15],tape:12,task:19,task_ev:[10,13],tea:12,techniqu:22,teeth:12,teh:22,tell:[10,15,22],tempor:21,ten:5,tent:12,term:5,test:[4,8,9,16],test_zscoring_comput:9,text:[13,16],tgime:[8,9],than:[5,10,12,13,16,17,19],thei:[5,7,12,13,14,17,21],them:[2,5,10,15],theori:13,therefor:10,theta:5,theta_avg_non_recal:4,theta_avg_recal:4,theta_sum_non_recal:4,theta_sum_recal:4,thi:[2,3,5,7,8,9,10,11,12,13,15,16,17,18,21,22],thin:[3,17],thing:[3,5,10],those:[15,16,19,21,22],though:[13,21],thr:[8,9,22],thread:[1,4,12],three:[5,10],thresh:5,threshold:5,thtw:16,thu:[4,15],thumb:[5,12],tichavski:5,tie:12,time:[1,2,3,5,9,10,12,14,16,17,22],time_axi:[8,9],time_axis_chop:8,time_axis_index:1,time_axis_long:8,time_axis_non_chop:8,time_seri:[1,8,9,10,16,18],timepoint:1,timeseri:[3,10,17,19],timeseriesx:[0,1,2,5,8,10,14,16,18,19,21],tip:7,titl:[13,16],tj011:15,tj011_06apr10_1319:15,tj011_event:15,to_hdf:[3,17],toad:12,toast:12,toe:12,togeth:22,toi:12,tol:16,too:22,took:12,tool:[12,19],toolkit:[16,22],tooth:12,top:[11,19],total:[3,8,9,16],total_number_of_item:[8,9],tpr:16,tpr_in:16,tpr_out:16,traceback:15,track:21,trai:12,train:[8,9,12,16],train_classifi:[8,9],training_classifi:8,training_data:16,training_featur:9,training_recal:9,training_session_mask:16,training_sesss:8,transform:[1,10,16],transpos:[5,8,9,16],transposed_log_pow_wavelet:[8,9],trash:12,treat:16,tree:12,trial:12,troubl:15,truck:[12,21],truli:3,truncat:16,ts1:22,tsm:22,tupl:[1,2,3,5,8,9],turn:13,tutori:[11,12,16,19],twice:5,two:[2,4,5,8,10,16,18,21],txt:10,type:[1,2,3,5,8,9,10,12,13,15,16,18,21,22],typeerror:15,typic:[5,21,22],ume:16,unabl:16,unavoid:5,under:[2,10,17,19],underli:13,unicod:3,uniform:[5,16,17],uniqu:[9,12,13,16],unit:[3,5,10,16,22],unknown:12,unless:5,unlik:5,until:5,unwant:[16,18],upsampl:1,usag:17,use:[1,2,3,5,7,8,9,10,11,15,16,17,18,19,20,21,22],use_reref_eeg:[2,10],use_session_chopp:8,use_session_chopper_for_wavelet:8,used:[2,3,5,9,15,16,19,21],useful:21,user:[2,8,9,10,16,21],uses:[3,7,12,16,21],using:[3,5,8,9,10,12,14,15,16,17,19,20,22],usual:10,util:[1,8,16],uwajd:5,v_1:[16,21],valid:[8,16,21],validation_auc:16,validation_classifier_data:8,validation_data:16,validation_featur:[8,9],validation_recal:[8,9],validation_recall_prob_arrai:[8,9,16],validation_recalled_ind:16,validation_recalls_arrai:16,validation_sess_max:16,validation_sess_min:16,validation_session_mask:16,validation_sesss:8,valu:[1,3,4,5,12,16,21],van:12,vararg:5,variabl:[11,16],varianc:[4,16],variou:[12,16,19,21],varkw:5,vase:12,vector:[4,5],verbos:[1,5,8,9,16],veri:[17,22],version:[5,8,16,19,20],vest:12,via:[13,15,17,19],view:[10,13,21],vine:12,visual:16,voltag:[10,16],volum:[10,12,13,15,21],vriabl:11,w_est0:5,w_est:5,w_tmp:16,wai:[5,9,12,13,17,18],wajd:5,wall:12,wand:12,want:[5,8,10,11,13,15,16,18,20,21],warm_start:16,warn:[5,10],wasobi:5,wave:[5,12,17],wavelet:[1,4,5,8,9,16,18],wcould:16,weai:22,web:12,wee:16,weed:12,weigh:5,weight:[4,5,16],well:[12,16,22],were:[15,21,22],west0:5,whale:12,what:[12,15,16,21,22],whatev:20,wheather:22,when:[2,3,4,5,8,9,10,15,16,17,19,20,21,22],where:[2,5,9,11,13,15,16,17,20],whether:[12,21],which:[2,3,4,5,8,9,10,12,13,16,21,22],whose:[5,12],wica:5,wica_clean:5,width:[1,13],window:[3,5],wing:21,without:[2,21],witj:16,word:[5,8,9,10,12,13,15,16,21],work:[3,5,13,14,19,21,22],workaround:12,worri:22,worth:2,woudl:22,woudld:16,would:[5,16,21],wrapper:[3,5,17],write:[3,7,12,16,20],writer:19,written:19,x_line:16,x_project:16,x_project_v:16,xarrai:[3,10,16,17,19,20,22],xarrat:22,xhigh:5,xlabel:[13,16],xlim:13,xlow:5,xrai:[16,18,21,22],xrang:[8,9],xtick:13,xticklabel:13,y_line:16,y_project:16,y_project_v:16,yard:15,yes:22,ylabel:[13,16],you:[2,3,5,8,9,10,11,13,15,16,17,18,19,20,21,22],your:[2,5,16,18,19,22],yourself:22,z_score:9,z_score_dict:8,z_score_mean_pow:[8,9],z_score_params_dict:8,zero:[5,8,16],zscore:[8,9,16],zscore_mean_pow:[9,16],zscore_mean_powers_alt:9,zscoreparam:8},titles:["ptsa.data","Filters","Readers","TimeSeriesX","Extension Modules","API Reference","&lt;no title&gt;","Development guidelines","Classifier time series","&lt;no title&gt;","Reading EEG Data from events","&lt;no title&gt;","BEHAVIORAL ANALYSES","1. pyFR","Examples","pyFR Demo","RAM Computational Pipeline","Basic <code class=\"docutils literal\"><span class=\"pre\">TimeSeriesX</span></code> functionality","Filtering Time Series","PTSA - EEG Time Series Analysis in Python","Installation","Interacting with RAM Data","PTSA Tutorial"],titleterms:{"function":17,"new":10,For:20,aggreg:22,analys:12,analysi:19,api:5,axes:22,baseeventread:21,basic:17,behavior:12,binari:20,built:20,butterworthfilt:18,circular_stat:4,classifi:8,cmleventread:21,comput:16,concaten:22,conda:20,data:[0,10,17,21],demo:15,depend:20,develop:7,deviat:22,dimens:17,dimension:22,eeg:[10,19,21],eegread:21,electrod:21,event:[10,21],exampl:14,extens:4,filter:[1,5,18],find:21,fr1:13,from:[10,20],guidelin:7,hdf5:17,helper:5,inform:21,instal:20,interact:21,jsonindexread:21,load:17,ltpfr2:[10,13],ltpfr:10,max:22,mean:22,min:22,modul:4,monopolartobipolarmapp:18,more:17,morlet:4,multi:22,netcdf:20,object:22,old:10,oper:22,option:20,other:[5,22],path:21,pipelin:16,pre:20,prerequisit:22,ptsa:[0,4,19,22],pyfr:[10,13,15],python:19,ram:[10,13,16,21],read:[10,21],reader:2,refer:5,resampl:17,save:17,seri:[8,18,19,21],sourc:20,standard:22,talread:21,test:7,time:[8,18,19,21],timeseriesx:[3,17,22],transpos:22,tutori:22,two:22,useful:22,using:21}})