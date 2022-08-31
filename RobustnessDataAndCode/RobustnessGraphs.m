%% Code for generating graphs for robustness analysis
%{
This code would use output from beta regressions in stata that is handcoded
into the current code for calculating graphs for robustness analysis
%}

%% graph controls
for swMr=0:1

    nVals=[100 10000]; %network size values
    numG=numel(nVals);
    if swMr
        kVals=[8 16];
        %kVals=[4:2:10];
    else
        kVals=[4:2:10]; % k values
    end
    numK=numel(kVals);
    dirNm='D:\Dropbox (Personal)\ComplexDiffusionPaper\Models and Stats';
    cd(dirNm);

    %% Create the regression model function
    if swMr
        BX=@(p1,p_ri,nl,kl)(-1.398*nl)+(23.71*p1)+(10.72*kl)+(-8.043*p_ri)+(1.196*nl.*p1)+...
            (-0.661*nl.*kl)+(0.214*nl.*p_ri)+(0.175*nl.*nl)+(-11.66*p1.*kl)+(2.726*p1.*p_ri)+...
            (-10.57*p1.*p1)+(3.076*kl.*p_ri)+(0*kl.*kl)+(1.273*p_ri.*p_ri)+(-8.125);
    else
        % this is currently the most likely version to work
        BX=@(p1,p_ri,nl,kl)(-1.392*nl)+(23.57*p1)+(20.56*kl)+(-3.806*p_ri)+(0.946*nl.*p1)+...
            (-0.457*nl.*kl)+(-0.337*nl.*p_ri)+(0.206*nl.*nl)+(-13.76*p1.*kl)+(2.765*p1.*p_ri)+...
            (-7.635*p1.*p1)+(0.666*kl.*p_ri)+(-3.522*kl.*kl)+(1.412*p_ri.*p_ri)+(-14.94);
    end
    PrdX=@(p1,p_ri,nl,kl)(1./(1+exp(-BX(p1,p_ri,nl,kl))))-0.5;


    %% define the input ranges for graphs

    [X,Y]=meshgrid(0:0.002:1,0:0.002:1);

    for i=1:numG
        Zsum=zeros(size(X));  %reset calculator
        g(i)=figure
        hold on
        for k=1:numK

            % calculate values
            Z=BX(Y,X,log10(nVals(i)),log10(kVals(k)));
            contour(X,Y,double(Z>0)*kVals(k),[kVals(k) 100],'ShowText','on')

            %{
        [C,h]=contour(X,Y,double(Z>0)*kVals(k),[kVals(k) 100],'ShowText','on')
        
        %drawnow();
        txt = get(h,'TextPrims');
        v = (get(txt,'String'));
        for ii=1:length(v)
            set(txt(ii),'String',['k=' v{ii}])
        end
        hold on
            %}
        end

        title(['N=' num2str(nVals(i)) ' Nodes'],'fontsize',16);
        ylabel('p_1','fontsize',14);
        xlabel('p_{ri}','fontsize',14);
        if swMr
            lbl='Mr';
        else
            lbl='1d';
        end
        print(g(i),['g-' lbl num2str(nVals(i)) ],'-djpeg','-r300');
        %  colormap(flipud(hot));
    end
end