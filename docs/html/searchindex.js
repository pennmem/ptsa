Search.setIndex({docnames:["api/data","api/data/filters","api/data/readers","api/data/timeseriesx","api/extensions","api/index","development","examples/eeg","examples/getting_started","examples/index","filters","index","ramdata"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":4,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,"sphinx.ext.intersphinx":1,nbsphinx:3,sphinx:56},filenames:["api/data.rst","api/data/filters.rst","api/data/readers.rst","api/data/timeseriesx.rst","api/extensions.rst","api/index.rst","development.rst","examples/eeg.ipynb","examples/getting_started.ipynb","examples/index.rst","filters.rst","index.rst","ramdata.rst"],objects:{"ptsa.data.filters":{ButterworthFilter:[1,0,1,""],MorletWaveletFilter:[1,0,1,""],MorletWaveletFilterCpp:[1,0,1,""],ResampleFilter:[1,0,1,""]},"ptsa.data.filters.ButterworthFilter":{filter:[1,1,1,""]},"ptsa.data.filters.MorletWaveletFilter":{filter:[1,1,1,""]},"ptsa.data.filters.ResampleFilter":{filter:[1,1,1,""]},"ptsa.data.readers":{BaseEventReader:[2,0,1,""],CMLEventReader:[2,0,1,""],EEGReader:[2,0,1,""],LocReader:[2,0,1,""],TalReader:[2,0,1,""]},"ptsa.data.readers.BaseEventReader":{as_dataframe:[2,1,1,""],find_data_dir_prefix:[2,1,1,""],modify_eeg_path:[2,1,1,""],normalize_paths:[2,1,1,""],read_matlab:[2,1,1,""]},"ptsa.data.readers.CMLEventReader":{modify_eeg_path:[2,1,1,""]},"ptsa.data.readers.EEGReader":{compute_read_offsets:[2,1,1,""],read_events_data:[2,1,1,""],read_session_data:[2,1,1,""]},"ptsa.data.readers.TalReader":{from_dict:[2,1,1,""],from_records:[2,1,1,""],get_bipolar_pairs:[2,1,1,""],get_monopolar_channels:[2,1,1,""],mkdtype:[2,1,1,""]},"ptsa.data.readers.edf":{edf:[2,2,0,"-"]},"ptsa.data.readers.edf.edf":{EDFRawReader:[2,0,1,""]},"ptsa.data.readers.edf.edf.EDFRawReader":{read_file:[2,1,1,""]},"ptsa.data.timeseries":{TimeSeries:[3,0,1,""]},"ptsa.data.timeseries.TimeSeries":{"var":[3,1,1,""],add_mirror_buffer:[3,1,1,""],all:[3,1,1,""],any:[3,1,1,""],append:[3,1,1,""],astype:[3,1,1,""],baseline_corrected:[3,1,1,""],coerce_to:[3,1,1,""],count:[3,1,1,""],create:[3,1,1,""],cumprod:[3,1,1,""],cumsum:[3,1,1,""],filter_with:[3,1,1,""],filtered:[3,1,1,""],from_hdf:[3,1,1,""],item:[3,1,1,""],max:[3,1,1,""],mean:[3,1,1,""],median:[3,1,1,""],min:[3,1,1,""],prod:[3,1,1,""],query:[3,1,1,""],reduce:[3,1,1,""],remove_buffer:[3,1,1,""],resampled:[3,1,1,""],searchsorted:[3,1,1,""],std:[3,1,1,""],sum:[3,1,1,""],to_hdf:[3,1,1,""]},"ptsa.extensions":{circular_stat:[4,2,0,"-"],morlet:[4,2,0,"-"]},"ptsa.extensions.circular_stat":{circ_diff:[4,3,1,""],circ_diff_par:[4,3,1,""],circ_diff_time_bins:[4,3,1,""],circ_mean:[4,3,1,""],compute_f_stat:[4,3,1,""],compute_z_scores:[4,3,1,""],single_trial_ppc_all_features:[4,3,1,"id0"]},"ptsa.extensions.morlet":{ChannelInfo:[4,0,1,""],EDFFile:[4,0,1,""]},"ptsa.extensions.morlet.EDFFile":{__init__:[4,1,1,""],get_channel_info:[4,1,1,""],get_channel_numbers:[4,1,1,""],get_samplerate:[4,1,1,""],read_samples:[4,1,1,""]}},objnames:{"0":["py","class","Python class"],"1":["py","method","Python method"],"2":["py","module","Python module"],"3":["py","function","Python function"]},objtypes:{"0":"py:class","1":"py:method","2":"py:module","3":"py:function"},terms:{"0":[1,2,3,4,7,8,12],"00":8,"001":[7,10],"002":[7,10],"003":[7,10],"003609":8,"004":[7,10],"005":[7,10],"005354":8,"006":7,"007":7,"008":7,"009":[7,10],"01":[7,8],"010":[7,10],"011":[7,10],"012":[7,10],"013":7,"014":7,"015":7,"016":7,"016682":8,"017":7,"018":7,"019":7,"02":7,"020":7,"021":7,"022":7,"023":7,"024":7,"025":7,"02586":8,"026":7,"027":7,"028":7,"028736":12,"029":7,"029344":8,"03":7,"030":7,"031":7,"032":7,"033":7,"034":7,"035":7,"036":7,"037":7,"037392":10,"038":7,"039":7,"040":7,"041":7,"042":7,"043":7,"044":7,"045":7,"046":7,"04690397":8,"047":7,"048":7,"049":7,"05":[7,12],"050":7,"051":7,"052":7,"053":7,"054":7,"055":7,"056":7,"057":7,"058":7,"059":7,"059196":12,"060":7,"061":7,"062":7,"063":7,"064":7,"070932":8,"071868":10,"072835":8,"07390804":8,"084708":10,"08995":12,"0hz":8,"0j":4,"0s":8,"0x11596a7d0":7,"0x1162587d0":7,"0x1162bfad0":7,"0x1167ecd10":7,"0x116b1cbd0":7,"0x2b7884cc0518":8,"0x2b78be4cc908":8,"0x2b78be58e320":8,"0x2b78be5e9a20":8,"0x2b78befd2d68":8,"0x2b78bfcc0b00":8,"0x2b78bfeb2ba8":8,"0x2b78c8143400":8,"0x2b78c92c8940":8,"0x2b78c94bc9e8":8,"1":[1,2,3,4,8,12],"10":[3,4,7,8,12],"100":[4,7,8,12],"1000":[4,8],"100521":12,"101":7,"101829":12,"102":7,"1020":[10,12],"103":7,"103113":12,"104":7,"106":7,"107":7,"108":7,"10hz":8,"11":[7,8,12],"110":7,"111":7,"111702":8,"112":7,"1128811":12,"1130002":12,"1131203":12,"114":7,"115":7,"116":7,"12":[7,8,12],"120":7,"121":7,"122":7,"123":[3,7],"123327":8,"125":7,"126":7,"127":7,"128":7,"129":7,"13":[7,8,12],"130":7,"131":7,"132":7,"132816":10,"133":7,"134":7,"135":7,"13522":10,"136":7,"138":7,"14":[7,8,12],"140":7,"141":10,"14164":10,"142":7,"143":7,"144":7,"1453499295325":12,"1453499297942":12,"1453499300510":12,"1453836066458":7,"1454447574230":12,"1454447576613":12,"1454447579014":12,"146":7,"147":7,"149":7,"15":[7,8],"153":7,"153828":12,"156":7,"15750319":8,"157676":10,"158":7,"16":[7,8],"160":7,"163":7,"163444":12,"165":7,"16645912":8,"167":7,"16746":12,"168":7,"169":[7,12],"17":[3,7,8,12],"170":7,"17307536":8,"178974":8,"18":[7,8],"1800":[10,12],"182":7,"183":7,"183362":7,"186":7,"188956":10,"189":7,"19":[7,8,12],"192":7,"194":7,"199":7,"1d":4,"1j":4,"2":[1,2,3,4,6,8,11,12],"20":[7,8,12],"200":[7,8],"2000":8,"203":7,"204":7,"20516":12,"21":[7,8,12],"210":7,"212":7,"214":7,"21464846":8,"215":7,"218":7,"22":[7,8],"222235":8,"22266263809965":12,"223432":10,"226":7,"23":[7,8],"232":7,"237":7,"24":[7,8],"243":7,"244184":8,"246":7,"247":7,"25":[7,8],"250":8,"251656":12,"255":7,"259":7,"26":[7,8],"261":7,"269":7,"27":[7,8],"272452":8,"273":7,"28":7,"282":12,"2841":7,"285444":8,"287":7,"289356":12,"28978477":8,"29":7,"291":7,"294":12,"296":7,"298972":12,"2hz":8,"3":[2,3,4,6,8,12],"30":7,"3000":8,"306184":12,"31":7,"312":7,"312604":12,"3128":12,"313":7,"3134":12,"3136":12,"3142":12,"3147":12,"315008":12,"3151":12,"3156":12,"31566":10,"3157":12,"3163":12,"3164":12,"3167":12,"3175":12,"319":7,"32":7,"321428":12,"3263":12,"3272":12,"3286":12,"33":7,"3341":10,"3343":12,"3351":12,"336389":8,"33666706":8,"3368":12,"34":[7,8],"3404":12,"3410":12,"3444":12,"3449":12,"3454":12,"3467":12,"3471":12,"3473":12,"35":7,"3512":12,"3513":12,"3519":12,"3580":12,"3581":12,"3588":12,"35896":10,"36":7,"3609":12,"3612":12,"368357":8,"37":7,"372158":8,"376608":10,"377922":8,"378594":8,"38":7,"384":7,"39":[7,8],"4":[1,3,4,7,8,10,12],"40":7,"406314":8,"41":7,"416":8,"42":7,"43":7,"431717":8,"4369":12,"44":7,"444":7,"447679e":8,"449":7,"45":7,"46":7,"46578":12,"47":7,"4722":12,"475753":8,"48":7,"48198941":8,"49":7,"497876":8,"499":8,"499296":10,"499759":8,"5":[1,3,4,7,8,12],"50":[7,8],"500":[7,8],"5000":8,"51":7,"513888":12,"517297":8,"52":7,"5211":12,"52192":12,"53":7,"535552":12,"54":7,"548364":12,"549016":10,"55":7,"57":7,"5749":12,"58":[7,10],"59":7,"59501017":8,"6":[1,3,7,8,12],"60":7,"61":7,"62":[7,10,12],"62199":8,"623764":12,"625":7,"63":7,"64":7,"6431":12,"65":7,"66":7,"67":[7,12],"673316":10,"68":7,"680535":8,"683395115":7,"69":7,"6hz":8,"7":[3,7,8,12],"70":7,"700748":12,"7009":10,"70154":12,"7022":10,"7061":10,"7063":10,"7067":10,"71":7,"710364":12,"7119":10,"7156":10,"7159":10,"7164":10,"7175":10,"7178":10,"7186":10,"72":7,"7221":10,"7227":10,"7228":10,"725608":12,"728804":12,"73":7,"73842":12,"74":7,"75":7,"76":7,"761696":12,"77":[7,12],"775328":12,"78":7,"7882":12,"79":[7,12],"8":[3,7,8,12],"80":7,"81":7,"813":12,"82":7,"821934e":8,"824685":8,"830037e":8,"84":7,"84015":12,"85":7,"853104":12,"86":7,"87":7,"874488e":8,"88":7,"8884":12,"89":7,"9":[3,7,8,12],"90":7,"901212":12,"91":7,"91326":12,"92":7,"93":7,"95":7,"958964":12,"96":7,"97":7,"970984":12,"99":7,"999":[2,7,8,12],"boolean":[2,4],"byte":[2,3],"case":[2,3,12],"class":[1,2,3,4,7,8,12],"default":[1,2,3,12],"do":[2,3,4,7,10,12],"float":[1,2,3,4,8],"function":[3,6,8,10,11,12],"import":[7,8,10,12],"int":[1,2,3,4],"long":8,"new":[1,2,3,6,8,11],"return":[1,2,3,4,7,8,12],"true":[1,2,3,7,8,12],"try":[2,8],"var":3,"void":3,"while":12,A:[1,2,3,4,8],As:[7,8,10],At:12,By:3,For:[3,8,10,12],If:[2,3,7,10,11,12],In:[8,12],It:2,NOT:12,Not:3,One:[2,3],The:[1,2,3,4,7,8,9,11,12],There:7,These:[4,7],To:[6,7,8,10,12],Will:7,With:[7,12],_____:12,__init__:[3,4],_filenam:2,about:[7,8,12],abov:12,acceler:4,access:[3,12],accordingli:3,account:2,accuraci:1,across:7,actual:[2,8,12],ad:[2,3,6,8,12],add:7,add_mirror_buff:3,addit:[1,3,7,11],adjac:7,advantag:4,after:[1,10,12],afterward:7,agagcl:4,against:3,aggregate_valu:[7,12],align:7,all:[2,3,6,7,8,10,11,12],all_ev:12,alloc:3,allow:[3,12],along:3,alreadi:6,also:[6,7,8,9,10,12],altern:[3,10,11],although:8,alwai:[3,12],amount:6,an:[2,3,4,7,8,10,11,12],anaconda3:8,analysi:[8,12],angl:4,angular:4,ani:[3,4,8,12],anoth:[2,3,8,10],anova:4,api:11,appear:3,append:3,appli:[1,3],applic:8,appropri:[3,10],ar:[2,3,4,6,7,8,9,12],arang:3,arbitrari:3,area:12,arg:[2,3],argument:[1,2,3,12],aris:3,arithmet:3,around:[3,4,7],arrai:[1,2,3,4,7,8,10,11,12],artifact:7,as_datafram:2,assertionerror:3,associ:[7,12],assum:[1,3,7],astyp:3,attach:2,attempt:3,attr:[3,7],attribut:[3,4,7,12],automat:2,avail:[3,9,12],averag:[3,4,7],avgsurf:12,awkward:3,ax:[3,7,8],axi:[1,3],b_filter:10,back:3,bad:2,band:10,bandstop:8,base:[2,3],base_e_read:12,base_eeg:[10,12],base_ev:12,base_rang:3,baseeventread:[2,7],basefilt:3,baselin:3,baseline_correct:3,baserawread:7,basic:[8,12],bdf:[2,4],bear:12,becaus:[3,8,11],becom:8,been:[2,3],befor:[6,10],begin:[3,7],behavior:7,being:3,belong:4,below:[9,10],besid:11,best:12,between:[7,8],beyond:4,bi:[2,12],big:4,bin:4,binari:[2,7],bipolar:[7,10,12],bipolar_eeg:7,bipolar_pair:[7,10,12],bool:[1,2,3],both:[1,3,8],bp_eeg:10,bp_eegs_filt:10,bp_eegs_filtered_1:10,bpdistanc:12,bptalstruct:[2,7],branch:6,broadcast:8,brodmann:12,buffer:[2,3,7,12],buffer_offset:2,buffer_tim:[2,7,12],build:[11,12],built:12,butterworth:[1,3,10],butterworthfilt:1,butterwoth:1,bw001:7,bw001_24jul02_0001:7,bw001_event:7,bw001_tallocs_database_bipol:7,c0:8,c1:4,c2:4,c6:8,c:[1,3,4,11],c_diff:4,calcul:[3,4],call:[3,10,11,12],callabl:3,can:[2,3,4,7,8,12],cannot:[3,8],care:8,cast:3,categori:11,catfr:2,caus:[2,3],cdiff_mean:4,cdot:4,cerebrum:12,certain:7,ch0:[2,7],ch1:[2,7],chang:[1,2,3],channel:[2,4,7,12],channel_nam:4,channelinfo:4,charact:7,cheatsheet:6,check:[8,12],choic:10,chunk:[2,3],circ_diff:4,circ_diff_par:4,circ_diff_time_bin:4,circ_mean:4,circular:4,circular_stat:5,classmethod:[2,3],clear:8,clearli:8,click:8,clone:11,clongdoubl:3,close:[3,8],cml:[7,12],cmleventread:[2,7],cmlreader:12,code:[2,3,6,12],coerc:3,coerce_to:3,collaps:12,color:8,column:[2,12],com:11,command:6,commit:6,common:2,common_root:[2,7],compar:4,comparison:8,compat:6,complet:1,complex:[1,4],compon:[7,10],compos:8,compress:3,comput:[1,4,10,11,12],compute_f_stat:4,compute_read_offset:2,compute_z_scor:4,concaten:[3,7,12],configur:12,conform:1,consid:8,consider:7,consist:[1,2],construct:[1,2,3,7,8,12],constructor:[3,12],contact:[2,12],contact_dict:2,contain:[1,2,3,7,8,10,12],contamin:7,content:3,context:8,contigu:3,control:3,conveni:[7,8,10,11,12],convers:3,convert:[2,12],convolut:4,coo:3,coord:[3,7,8],coordin:[3,7],copi:[2,3],cord:12,core:2,correct:3,correspond:[7,8],correspong:2,could:[7,8,12],count:3,cpu:1,creat:[3,7,10,12],create_dataset:3,crteat:10,cumprod:3,cumsum:3,cumvalu:3,current:2,current_process:7,cycl:8,d:[3,11],da:3,darpa:12,dask:3,data1:[2,8,12],data2:[2,8,12],data3:8,data:[1,2,3,4,5,6,9,10,11],data_kwarg:3,dataarrai:[3,7,10,11],databas:2,datafil:2,datafram:[2,3],dataroot:2,dataset:3,datetime64:3,deal:3,decompos:10,decomposit:[1,4],defin:[3,10,11],definit:7,depend:3,deprec:12,describ:[1,12],desir:3,detail:3,determin:[2,12],develop:11,dict:[2,3],dictionari:[2,3],did:7,differ:[2,3,4,7,10],dig_max:4,dig_min:4,digit:4,dim:[3,8],dimens:[1,2,3,4,7,8],dimension:7,dir:2,dir_prefix:2,directli:6,directori:[2,7,12],discuss:12,disk:3,divid:4,document:3,doe:[3,11],don:6,done:3,door:12,doubl:8,downsampl:8,drop:[2,8],dtype:[2,3,4,7,12],due:7,durat:3,e:[2,3,4,8,12],e_path:12,each:[2,3,4,7,12],earli:8,early_t:8,easili:8,ecog:7,edf:[2,5],edffil:4,edflib:4,edfrawread:[2,4],edg:[3,8],eeg:[2,4,9,10],eeg_fname_replace_pattern:[2,12],eeg_fname_search_patt:2,eeg_fname_search_pattern:[2,12],eeg_read:12,eegeffset:2,eegfil:[2,7,12],eegoffset:[7,12],eegread:[2,7],effect:[3,8],effici:12,either:[2,3,4],electrod:[4,7,10],element:[2,3],elimin:[7,12],eliminate_events_with_no_eeg:[2,12],eliminate_nan:2,empti:[2,4],enam:12,encod:3,end:[2,3,7,8],end_offset:2,end_tim:[2,7,12],engin:3,ensur:12,entir:2,entri:[2,3,12],env:[7,8],envelop:4,ephi:7,equiv:3,equival:3,error:8,es:3,etc:[2,4,11,12],etyp:12,european:2,eval:3,evalu:3,even:[8,12],event:[2,9,10,11],event_path:12,events_all_ltp093:7,everi:[2,8],exact:8,exactli:12,exampl:[2,3,4,7,8,10,11,12],except:[1,3,8],exist:6,exp_vers:7,expect:12,experi:[7,12],experiment:12,explicitli:2,express:[2,3],expvers:12,exract:2,extend:8,extens:[2,5],extra:[2,12],extract:12,f8:[7,12],f:[3,4,7],f_stat:4,facilit:[11,12],fact:[10,12],factori:3,fall:3,fals:[1,2,3,7,12],famili:4,fastpath:3,featur:8,few:7,fewer:3,fftw:4,field:[2,3,7,12],fig:8,figsiz:8,figur:8,file:[2,3,4,7,11,12],filenam:[2,3,4,7,12],fill:4,filt_typ:[1,3,8,10],filter:[0,3,4,5,7,11],filter_class:3,filter_with:3,filtered_data:8,find:[3,7],find_data_dir_prefix:2,find_dir_prefix:2,first:[4,7,8,10,12],fix:7,flag:[1,2],flat:[2,3],flat_df:2,flatten:3,flexibl:8,float32:3,float64:[3,7,8],fname:8,focu:8,folder:2,follow:[2,3,4,7,8,11,12],forc:3,form:[3,10],format:[2,4,7,8,11,12],fortran:3,found:7,fourier:3,fr1:[7,12],frac:4,framework:12,freq1:8,freq2:8,freq3:8,freq:1,freq_rang:[1,3,10],frequenc:[1,3,4,8,10],frequency1:8,frequency2:8,from:[1,2,3,4,8,9,10,12],from_dict:2,from_hdf:[3,8],from_record:2,fstat:4,full:[2,3],func:3,further:11,futur:[6,12],g:[2,3,4,12],gain:7,gaussian:4,gener:12,get:[2,7,9,10,12],get_bipolar_pair:[2,7,12],get_channel_info:4,get_channel_numb:4,get_monopolar_channel:[2,7,12],get_sampler:4,get_valu:7,git:11,github:11,give:[7,8],given:[2,3,4,8],go:7,got:8,grai:12,greatest_environ:8,grpname:12,gt:[7,8],guard:3,guidelin:11,gyru:12,h5:8,h5netcdf:11,h5py:[3,8],ha:[2,3,7,8,11,12],had:3,half:2,hand:12,handl:2,hashabl:3,hat:4,have:[2,3,4,7,10,12],hdf5:[3,8],heavili:7,help:7,helper:2,here:[8,9,10,12],high:8,high_freq:4,higher:[4,8],highest:8,highpass:8,home1:8,how:[2,8,12],howev:[7,8,12],hte:2,http:11,hz:[3,7],i8:[7,12],i:[3,4,12],ident:4,ignor:3,illustr:8,implement:[2,3],includ:[2,4,6],inclus:3,index:[2,3,10,12],indexread:7,indic:[1,2,3,4,12],individu:[2,12],indivsurf:12,inform:[2,3,4,7],infrom:12,inherit:8,initi:[10,12],inlin:7,input:[1,2,3,10,11],insert:3,insid:10,instal:8,instanc:[3,8,10,12],instead:[3,6,8,12],instruct:12,int16:7,int_typ:3,integ:[2,3],interact:11,interest:[3,7],interfac:[4,7],intern:[3,12],interpret:3,interv:12,introduct:11,intrus:[7,12],invari:2,involv:6,is_stim:7,isel:3,isstim:12,issu:2,item:[3,7,12],item_nam:7,item_num:7,itemno:[7,12],iter:[1,3],its:[3,8,10],itself:8,iwt:4,job:10,join:2,jr:[7,12],json:[2,7,12],json_dict:2,jsonindexread:7,juic:7,jupyt:9,k:3,keep:[3,8],keep_attr:3,keepdim:3,kei:[2,3],kept:[1,12],keyword:[1,2,3,12],khz:3,kind:3,know:[2,12],kwarg:[2,3],lab:[7,12],label:[2,3,4,7,8],larg:6,last:8,late:8,late_t:8,later:8,latest:11,launch:1,layout:3,lead:[2,3],learn:[8,11],least:3,leav:3,left:[3,12],legaci:[3,6],legend:8,len:4,length:[2,3,4],leond:7,let:[7,10,12],level:[3,4],lib:[7,8],librari:[4,11],like:[1,2,3,4,7,8,11,12],line2d:[7,8],line:[6,7,8],linspac:8,list:[1,2,4,7,12],liter:7,liyuxuan:8,ll:[7,8,11],load:[3,7,12],lobe:12,loc1:12,loc2:12,loc3:12,loc4:12,loc5:12,loc6:12,local:2,locat:[7,12],locread:2,loctag:12,longdoubl:3,look:[7,11,12],loop_axi:3,lose:[3,8],losspass:8,low:[4,8],low_freq:4,lower:8,lowest:[3,8],lowpass:8,lpog10:12,lpog11:12,lpog12:12,lpog13:12,lpog14:12,lpog1:12,lpog2:12,lpog3:12,lpog4:12,lpog5:12,lpog6:12,lpog7:12,lpog9:12,lpog:12,lsag:12,lt:[7,8],ltp:7,m2b:10,m:[2,4,6],magnitud:4,mai:[3,10,12],main:[3,7,11],maintain:3,make:[3,6,10,11],mani:[8,12],manipul:[8,12],mark:[3,6,7],mask:2,master:6,mat:[2,7,12],match:[3,12],math:3,matlab:[2,12],matplotlib:[7,8],matrix:4,matter:[10,12],max:3,max_freq:1,maximum:4,mean:[1,2,3,7,8],median:3,memori:[3,7,12],merg:6,metadata:3,meth:2,method:[2,3,7,8,10,12],mid:8,middl:[8,12],might:[2,7],millisecond:3,min:3,min_count:3,min_freq:1,miniconda2:7,minimum:4,mirror:3,miss:[2,3],missing_dim:3,mkdtype:2,mode:3,modern:6,modifi:[6,11],modify_eeg_path:2,modul:[5,12],mono:12,monopolar:[2,10,12],monopolar_channel:12,monopolartobipolarmapp:7,montag:[7,12],more:[7,8],morlet:[1,5],morletwaveletfilt:1,morletwaveletfiltercpp:[1,4],morletwavelettransform:4,most:[8,12],mount:[2,12],movement:7,msoffset:[7,12],mstime:[7,12],much:12,multi:7,multidimension:8,multiphasevec:4,muscl:7,must:[2,3,4,6],my:12,my_ts_data:8,n:[4,11],n_bp:4,n_freq:4,n_perm:4,n_thread:4,na:3,name:[1,2,3,4,8,12],nan:[2,3,12],ncol:8,nd:3,ndarrai:[1,2,3],need:[3,8,11,12],neither:3,nest:2,netcdf4:11,newli:3,next:[7,12],nf:4,no_reref:12,nois:[7,8],noisi:8,non:[2,3,8],none:[2,3,4],nonreref:2,noreref:[2,7,12],normal:12,normalize_eeg_path:[2,12],normalize_path:2,note:[2,3,7,8],notebook:[7,8,9],noth:3,notic:10,now:[1,3,12],np:[1,2,3,4,7,8],num_mp_proc:3,num_point:8,number:[1,2,3,4,7,12],numexpr:3,numpi:[2,3,7,8,11,12],o:3,oar:12,obj:3,object:[1,2,3,4,7,10,11,12],observ:[4,8],obtain:12,occur:3,occurr:2,offer:8,offset:[2,4,12],ommit:12,onc:[7,10],one:[2,3,4,7,8,10,12],ones:[2,6],onli:[3,4,7,8,12],onset:12,open:[2,11],oper:[3,8,10,11],operand:8,optim:3,option:[3,6],order:[1,2,3,4,8,10,12],ordereddict:7,organ:12,origianl:8,origin:[1,2,3,8],ot:12,other:[1,3,7,8,12],otherwis:3,our:[7,8,12],ourselv:7,out:[1,3,7,10,12],output:[1,10,11,12],output_dim:1,outsample_featur:4,outsid:8,outsourc:12,over:[1,3,4,7,8],overlap:8,overrid:3,own:8,packag:[7,8,10,11],pad_to_pow2:3,page:9,pair:[2,7,10,12],pairs_path:7,pairwis:10,panda:[2,3],parallel:[1,4],param:[2,7],paramet:[1,2,3,4,7,10,12],paramsread:7,pars:3,parser:3,part:4,partial:2,particular:12,partit:4,pass:[3,7,10,12],path:[2,3,7],pattern:2,pd:2,peak:4,pennmem:11,per:3,perform:[3,4,7,8,11],period:[2,3,7],perserv:8,persist:7,phase:[1,4],phase_diff:4,phi:4,phys_max:4,phys_min:4,physdimens:4,physic:4,pi:[4,8],place:[2,3,8],plot:[7,8],plt:[7,8],point:[2,3,4,7,8,12],pool:1,popul:12,possibl:[3,11],pow_mat:4,power:1,ppc_output:4,precis:8,prefer:10,prefilt:4,prefix:2,present:[2,3,6],preserv:3,prevent:3,previou:12,print:[1,7,8,12],procedur:12,process:[6,12],prod:3,produc:8,project:12,proper:1,properti:12,protocol:[7,12],provid:[3,4,7,11,12],psi:4,ptsa:[1,2,3,5,6,7,9,10,12],pull:6,purpos:[7,8],py:[2,7,8,11],pyplot:[7,8],pytest:6,python2:7,python3:8,python:[3,6,12],queri:[3,12],queries_kwarg:3,quickli:4,r1060m_event:2,r1111m:[7,12],r1111m_event:12,r1111m_fr1_0_22jan16_1638:12,r1111m_fr1_2_26jan16_1408:7,r1111m_fr1_3_02feb16_1528:12,r1111m_tallocs_database_bipol:12,r1:[7,12],r:2,rais:3,ram:11,ram_fr1:[2,12],randint:3,random:[3,8],rang:[1,3,7,8,10],rate:[1,2,3,8],rather:[7,11],rawbinwrapp:2,re:7,read:[2,4,8,9,11],read_events_data:2,read_fil:2,read_matlab:2,read_sampl:4,read_session_data:2,read_siz:2,reader:[0,4,5,7,11,12],readi:12,real:8,realli:7,reason:3,rec:12,recal:[4,7,8,12],recarrai:[2,3,7,12],recommend:11,record:[2,4,7,12],rectim:[7,12],recurs:2,reduc:3,reduct:3,refer:[11,12],referenc:7,rel:[7,12],relationship:8,relev:8,remov:[1,2,3,7,10,12],remove_bad_ev:2,remove_buff:[3,7],renam:1,repalc:2,repeatedli:3,replac:[2,3,7,12],repositori:11,repres:[2,11],represent:4,request:[3,6],requir:[1,3,6],reref:[2,12],rereferenc:7,resampl:[1,3],resampled_r:[3,8],resamplefilt:1,resampler:1,reset:3,reshap:4,result:[3,4,8,10],retain:3,retriev:7,reus:1,rhino:[2,7],rhino_root:[7,12],root:2,round:[1,4],round_to_original_timepoint:1,run:[6,10],runner:6,runtimewarn:7,s256:[7,12],s3:[2,7],s:[3,7,10,12],safe:3,same:[1,2,3,4,8,12],same_kind:3,sampl:[1,2,3,4,8],sample_freq:4,sample_r:8,sampler:[3,7,8],satisfi:3,save:3,scalar:[2,3],scalp:7,scalp_ev:2,scheme:2,scipi:11,screen:12,search:2,searchsort:3,second:[2,3,4,7,8,12],section:[8,12],see:[3,8,12],seed:3,seem:7,segment:12,sel:[7,8],select:[3,8,12],self:2,semant:3,semi:2,sentinel:[3,12],separ:6,sequenc:3,seri:[1,2,3,8],serial:3,serialpo:[7,12],sess_start:7,session:[2,7,12],session_dataroot:2,set:[1,2,3,7,10,12],set_xlabel:8,set_ylabel:8,setup:11,sever:11,shape:[4,8],sharei:8,sharex:8,should:[1,2,3,4,7,8],show:[8,10],shz:8,side:[3,4],sigma:4,signal:[2,4,7,8,10,11,12],signal_len:4,significantli:11,similar:3,simpl:10,simpli:8,simplifi:11,sin:8,sinc:[8,12],singl:[3,12],single_trial_ppc_all_featur:4,sinunoid:8,sinusoid:8,site:[7,8],size:3,skip:3,skipna:3,slightli:[3,4],slow:6,small:1,smooth:11,smp_in_datarecord:4,smp_in_fil:4,so:[3,6,7,12],some:[3,6,7,12],someth:10,sometim:8,sort:12,sorter:3,spars:3,specif:[7,8,11,12],specifi:[2,3,4,8,10,12],spectra:1,speed:[3,4,7],stack:8,stand:12,standard:[1,3],star:7,start:[2,3,9,10,12],start_offset:2,start_tim:[2,7,12],statement:3,statist:11,std:3,step:11,stim_list:7,stim_param:[2,7],stimamp:12,stimanod:12,stimanodetag:12,stimcathod:12,stimcathodetag:12,stimlist:12,stimloc:12,stop:[1,3,8,10,12],store:[2,4,7,12],str:[1,2,3,4,8],strict:3,string:[1,3,7],struct:2,struct_nam:2,struct_typ:[2,12],structur:[2,12],sub:3,subclass:[3,7,11],subfield:2,subject:[7,12],submit:6,subok:3,subplot:8,subsequ:12,subset:8,subtract:[2,3,8],successfulli:2,suffer:8,suffix:7,suitabl:3,sum:[3,8],summar:3,suppli:3,support:3,suppos:8,sure:3,swig:11,syntax:[3,10,12],system:7,t:[2,4,6,8],tagnam:12,take:[2,4,7,10,11],tal:[2,7,12],tal_path:12,tal_read:[7,12],tal_struct:12,talread:[2,7],task_ev:7,technic:8,tell:7,tempor:12,test:4,text:8,than:[3,7,8,11],thei:[6,9,12],them:[2,3,7,8],therefor:[7,8],theta_avg_non_recal:4,theta_avg_recal:4,theta_sum_non_recal:4,theta_sum_recal:4,thi:[2,3,4,6,7,8,10,12],thin:3,thing:[4,7,8],those:12,though:[8,12],thread:[1,4],three:7,through:[3,8],thu:[4,8],time:[1,2,3,7,8],time_axis_index:1,time_axis_nam:1,time_seri:[1,7],timedelta64:3,timepoint:[1,8],timeseir:8,timeseri:[0,1,2,5,7,9,10,11,12],timeserid:8,timeseriesx:7,timestamp:8,tip:6,to_hdf:[3,8],togeth:8,tool:[11,12],top:[3,11],total:3,track:[8,12],transduc:4,transform:[1,4,7],transformed_sign:4,transpos:8,tree:3,tri:3,truck:12,ts:[3,8],ts_transpos:8,tupl:[2,3],tutori:11,two:[2,4,7,8,10,12],txt:7,tyep:2,type:[1,2,3,4,7,10,12],typecod:3,typeerror:3,typic:12,unchang:3,under:[2,7],underli:[3,8],undesir:8,unfilt:8,uniform:8,union:[1,2],unit:[3,4,7],unless:3,unmatch:8,unpack:2,unsaf:3,unwant:10,up:3,updat:8,us:[1,2,3,4,6,7,9,10,11],use_reref_eeg:[2,7],user:[2,7,12],userwarn:8,usual:7,util:[1,4,12],v:3,v_1:12,valid:[3,12],valu:[3,4,8,12],vari:8,variabl:[3,4],varianc:4,variou:[11,12],vector:4,verbos:1,veri:[3,8],version:[1,3,8,11,12],versionchang:1,via:11,view:[7,12],visual:8,voltag:7,volum:[7,12],vstack:8,w:[2,3,4],wa:[1,2],wai:[10,11,12],walk:8,want:[7,8,10,11,12],warn:[3,7,8],wavelet:[1,4,10],we:[2,7,10,12],weight:4,well:8,were:12,what:[3,8,12],when:[1,2,3,4,7,12],where:[2,3,4],whether:[2,12],which:[1,2,3,4,7,12],whose:2,widehat:4,width:[1,4],window:3,wing:12,within:3,without:[2,3,8,12],word:[7,12],work:[3,9,12],worth:2,would:[3,12],wouldn:8,wrap:3,wrapper:[3,4,8],write:[6,11],x:[2,3,4,7,12],xarrai:[3,7,8,11],xr:3,xrai:[10,12],y:[4,11,12],ylim:8,you:[2,3,7,10,11,12],your:[2,10],z:[3,4,12],zero:[1,8],zoom:8},titles:["ptsa.data","Filters","Readers","TimeSeries","Extension Modules","API Reference","Development guidelines","Reading EEG Data from events","Getting started with timeseries","Examples","Filtering Time Series","PTSA - EEG Time Series Analysis in Python","Interacting with RAM Data"],titleterms:{"1":7,"2":7,"3":7,"new":7,For:11,There:8,analysi:11,api:5,baseeventread:12,binari:11,built:11,butterworthfilt:10,circular_stat:4,cmleventread:12,compon:8,conda:11,content:11,coordin:8,creat:8,data:[0,7,8,12],depend:11,develop:6,differ:8,each:8,edf:4,eeg:[7,11,12],eegread:12,electrod:12,event:[7,12],exampl:9,extens:4,filter:[1,8,10],find:12,from:[7,11],get:8,guidelin:6,have:8,index:8,inform:12,instal:11,interact:12,io:11,jsonindexread:12,let:8,load:8,ltpfr2:7,ltpfr:7,match:8,modul:4,monopolartobipolarmapp:10,morlet:4,netcdf:11,now:8,object:8,old:7,option:11,out:8,path:12,pre:11,ptsa:[0,4,8,11],pyfr:7,python:11,ram:[7,12],re:8,read:[7,12],reader:2,readi:8,refer:5,resampl:8,roll:8,s:8,save:8,seri:[10,11,12],some:8,sourc:11,start:8,talread:12,test:6,three:8,time:[10,11,12],timeseri:[3,8],us:[8,12],we:8,you:8,your:8}})