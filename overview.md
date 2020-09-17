
demo:
{	
	[]
	
	handleEvents:
	{
		[]
		
<-<-<-<-<-<-<-	exit "select": [-]

		move <> /\ \/:
		{
			[
			Trackingmode,
			ExternalCollisionProtection
			]
		
		}
		
			
		guidedMove:
		{
			[
			Trackingmode,
			Awareness,
			ExternalCollisionProtection,
			BackgroundMovement,
			?CollisionProtection?
			]
		
			holdCustomPose:
			{
				[
				Life
				BackgroundMovement
				]
			}
		
		
		}
	
		alignHit: 
		{
			[
			Trackingmode
			ExternalCollisionProtection,
			?CollisionProtection?
			]
			
			holdCustomPose:
			{
				[
				Life
				BackgroundMovement
				]
			}
			
			align:
			{
				[
				Trackingmode
				?Security distance?
				?ExternalCollisionProtection?
				]
			
			}
			
			animate:
			{
				[
				Trackingmode
				ExternalCollisionProtection,
				CollisionProtection,
				?BackgroundMovement?
				]
			}
			
		}		
	}
}


















