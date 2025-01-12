SELECT DISTINCT co.[abn] ,co.[Registration Date], dbo.[fProperCase](co.[charity name],'|APT|HWY|BOX|',NULL) as [Charity Name],co.[charity website], co.[charity size], co.[financial report date received], co.[staff - full time], co.[staff - part time],
co.[staff - casual],co.[total full time equivalent staff], co.[staff - volunteers],co.[charity has related party transactions],co.[grants and donations made for use in Australia],
co.[grants and donations made for use outside Australia],co.[total expenses],co.[net surplus/deficit], dbo.[fProperCase](ca.[Address],'|APT|HWY|BOX|',NULL) as [Address], dbo.[fProperCase](ca.[Town_City],'|APT|HWY|BOX|',NULL) as [Town_City], 
CASE WHEN cs.[state] IS NULL THEN ca.[State] ELSE cs.State END as State, dbo.[fProperCase](cp.[Classification],'|APT|HWY|BOX|',NULL) as [Classification], dbo.[fProperCase](cp.[Purpose],'|APT|HWY|BOX|',NULL) as [Purpose], cg.[Latitude], cg.[Longitude]
FROM [dbo].Charity_Operations co
LEFT JOIN dbo.Charity_State cs ON co.abn = cs.ABN
LEFT JOIN [dbo].[Charity_Address] ca ON ca.ABN = co.abn AND ca.ABN = cs.ABN
LEFT JOIN [dbo].[Charity_Programs] cp ON cp.ABN = co.abn AND ca.ABN = cp.ABN AND cs.ABN = cp.ABN
LEFT JOIN [dbo].[Charity_Geography] cg ON cg.ABN = co.abn AND cg.ABN = cs.ABN AND cg.ABN = ca.ABN AND cg.ABN = cp.ABN