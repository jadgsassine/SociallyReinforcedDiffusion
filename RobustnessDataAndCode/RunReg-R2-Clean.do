*code for replicating the robustness analysis reported in the paper's online supplement
clear
ssc install outreg2
import delimited "D:\Dropbox (Personal)\ComplexDiffusionPaper\Models and Stats\raw_data_lattice_final.csv"
gen y1=(y+2)/2.68
rename netw_size nz
gen n=nz*nz
gen nl=log10(n)
gen kl=log10(k*2)
gen z1=max_random>0.5
gen z2=max_random*0.999+0.0005

* all variables and no interactions
betareg z2 p1 kl p_ri nl p_si p_sw if (max_random>0.5 | max_cluster>0.5)
predict prd2
corr prd2 z2
scatter z2 prd2

* 4 variables and all interactions ; this is the primary model to use for graphs
betareg z2 c.nl##c.(p1 kl p_ri nl) c.p1#c.(kl p_ri p1) c.kl#c.(p_ri kl) c.p_ri#c.p_ri if (max_random>0.5 | max_cluster>0.5)
outreg2 using regressionresults2, replace excel
predict prd1
corr prd1 z2
scatter z2 prd1



* working on the moore dataset
clear
import delimited "D:\Dropbox (Personal)\ComplexDiffusionPaper\Models and Stats\raw_data_moore_final.csv"
drop if y==0
gen y1=(y+2)/3.91
rename netw_size nz
gen n=nz*nz
gen nl=log10(n)
gen kl=log10(k*2)
gen z1=max_random>0.5
gen z2=max_random*0.999+0.0005
order y1 p1 p_ri kl nl p_sw p_si

* all variables and no interactions 
betareg z2 p1 kl p_ri nl p_si p_sw if (max_random>0.5 | max_cluster>0.5)
predict prd2
corr prd2 z2
scatter z2 prd2

* 4 variables and all interactions ; this is the primary model to use for graphs
betareg z2 c.nl##c.(p1 kl p_ri nl) c.p1#c.(kl p_ri p1) c.kl#c.(p_ri kl) c.p_ri#c.p_ri if (max_random>0.5 | max_cluster>0.5)
outreg2 using regressionresults2, replace excel
predict prd1
corr prd1 z2
scatter z2 prd1

