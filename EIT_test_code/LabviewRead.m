function [data] = LabviewRead(fname)
%LABVIEWREAD 
fid=fopen(fname);
datacell=textscan(fid,'','CommentStyle','#','CollectOutput',1);
data=datacell{1};
fclose(fid);
end

