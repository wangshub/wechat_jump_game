raw=imread('1.jpg');
%提取R通道的数值
raw_r=raw(:,:,1);
imshow(raw_r);

label1=0;
label1val=0;

label1num=0;
label1min=0;
label1max=0;

currentPIXval=0;

imshow(raw);
%720:900
for i=720:1000
    
    label1=0;
    label2=0;
    label3=0;
    label4=0;

    label1val=0;
    label2val=0;
    label3val=0;
    label4val=0;
    
    
    label1min=0;
    label1max=0;
    
    findmaxflag=1;
    
    for x=1:1080
        cur=raw_r(i,x);
        if((cur>label1val-15)&&(cur<label1val+15))
            label1=label1+1;
            if(findmaxflag)
                if(x-label1min>10)
                    label1max=x;
                    findmaxflag=0;
                else
                    label1min=x;
                end
            end
        
        continue;
        end

        
        if(label1val==0)
            label1val=cur;
            continue;
        end    
    end
    if(abs(label1max-label1min)<1080)
        if(label1max-label1min<=label1num&&(label1max-label1min>20))
            print (label1max+label1min)/2
            hold on;
            plot((label1max+label1min)/2,i,'+','MarkerSize',20);
            break;
        end
        label1num=label1max-label1min;
    end

end


