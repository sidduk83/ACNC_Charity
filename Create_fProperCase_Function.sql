USE [SK1259]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE FUNCTION [dbo].[fProperCase](@Value varchar(8000), @Exceptions varchar(8000),@UCASEWordLength tinyint)
returns varchar(8000)
as

begin
      declare @sep char(1) 
      declare @i int 
      declare @ProperCaseText varchar(5000)
      declare @Word varchar(1000)
      declare @IsWhiteSpace as bit
      declare @c char(1) 

      set @Word = ''
      set @i = 1
      set @IsWhiteSpace = 1
      set @ProperCaseText = ''
      set @sep = '|'


      if @UCASEWordLength is null set @UCASEWordLength = 1

      set @Value = LOWER(@Value)

      while (@i <= len(@Value)+1)
      begin

            set @c = SUBSTRING(@Value,@i,1)

            if @IsWhiteSpace = 1 set @c = UPPER(@c)

            set @IsWhiteSpace = case when (ASCII(@c) between 48 and 58) then 0
                                          when (ASCII(@c) between 64 and 90) then 0
                                          when (ASCII(@c) between 96 and 123) then 0
                                          else 1 end

            if @IsWhiteSpace = 0
            begin
                  set @Word = @Word + @c
            end
            else
            begin

                  set @Word = case when len(@Word) <= @UCASEWordLength then UPPER(@Word) else @Word end


                  set @Word = case when charindex(@sep + @Word + @sep,@exceptions collate Latin1_General_CI_AS) > 0
                                    then substring(@exceptions,charindex(@sep + @Word + @sep,@exceptions collate Latin1_General_CI_AS)+1,len(@Word))
                                    when @Word = 's' and substring(@Value,@i-2,1) = '''' then 's'
                                    when @Word = 't' and substring(@Value,@i-2,1) = '''' then 't'
                                    when @Word = 'm' and substring(@Value,@i-2,1) = '''' then 'm'
                                    when @Word = 'll' and substring(@Value,@i-3,1) = '''' then 'll'
                                    when @Word = 've' and substring(@Value,@i-3,1) = '''' then 've'
                                    else @Word end

                  set @ProperCaseText = @ProperCaseText + @Word + @c
                  set @Word = ''
            end
            set @i = @i + 1
      end
      return @ProperCaseText
end