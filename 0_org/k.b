/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2312                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      k;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 8.5e-4; //inetnsity I=10%, vel=0.4m/s, 2.57e-3 //4.14e-03; //$turbulentKE;

boundaryField
{
    //inletWater
    "inletWater.*"
    {
        type            fixedValue;
        value           $internalField;
    }
    inletSediment
    {
        type            fixedValue;
        value           $internalField;
        //type            zeroGradient;
    }

    outletWater
    {
        type            inletOutlet;
        inletValue      $internalField;
        value           $internalField;
    }
    outletSediment
    {
        type            inletOutlet;
        inletValue      $internalField;
        value           $internalField;
    }
    top
    {
        type            inletOutlet;
        inletValue      $internalField;
        value           $internalField;
    }
    "(sideWalls|bottom|pier)"
    {
        type            kqRWallFunction;
        value           $internalField;
    }

}


// ************************************************************************* //
