package CanSatViews {
    part def CS1 {
        part power : Power;
        part sensors : Sensors;
    }
    part def Power;
    part def Sensors;

    view existingView : StandardViewDefinitions::GeneralView {
        expose CanSatViews::CS1;
    }
}
