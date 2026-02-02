
vehicle(small_vehicle).
vehicle(large_vehicle).
vehicle(plane).
vehicle(ship).
vehicle(helicopter).

sports_facility(tennis_court).
sports_facility(basketball_court).
sports_facility(soccer_ball_field).
sports_facility(baseball_diamond).
sports_facility(swimming_pool).
sports_facility('Ground_Track_Field').

infrastructure(harbor).
infrastructure('Bridge').
infrastructure(roundabout).
infrastructure(storage_tank).


%% ==============================================================================
%% RULE SET 1: CONFIDENCE BOOSTING (Weight > 1.0)
%% Based on strong, positive correlations in facts.pl
%% ==============================================================================

%% fact('cooccurs', 'harbor', 'ship', 951450).
confidence_modifier(ship, harbor, 1.25).
confidence_modifier(harbor, ship, 1.25).

confidence_modifier(helicopter, ship, 1.20).
confidence_modifier(ship, helicopter, 1.20).

%% fact('adjacent_to', 'large_vehicle', 'small_vehicle', 67014).
confidence_modifier(large_vehicle, small_vehicle, 1.15).
confidence_modifier(small_vehicle, large_vehicle, 1.15).

confidence_modifier(FacilityA, FacilityB, 1.10) :-
    sports_facility(FacilityA),
    sports_facility(FacilityB),
    FacilityA \= FacilityB.

%% fact('cooccurs', 'roundabout', 'small_vehicle', 17566).
confidence_modifier(small_vehicle, roundabout, 1.10).
confidence_modifier(roundabout, small_vehicle, 1.10).


%% ==============================================================================
%% RULE SET 2: PLAUSIBILITY PENALTIES (Weight < 1.0)
%% ==============================================================================

confidence_modifier(ship, 'Bridge', 0.1).
confidence_modifier('Bridge', ship, 0.1).
confidence_modifier(ship, roundabout, 0.1).
confidence_modifier(roundabout, ship, 0.1).

confidence_modifier(plane, harbor, 0.2).
confidence_modifier(harbor, plane, 0.2).
confidence_modifier(plane, 'Bridge', 0.2).
confidence_modifier('Bridge', plane, 0.2).

confidence_modifier(large_vehicle, roundabout, 0.75).
confidence_modifier(roundabout, large_vehicle, 0.75).

confidence_modifier(Infra, Facility, 0.7) :-
    infrastructure(Infra),
    sports_facility(Facility).
confidence_modifier(Facility, Infra, 0.7) :-
    sports_facility(Facility),
    infrastructure(Infra).

confidence_modifier(Vehicle, Facility, 0.5) :-
    vehicle(Vehicle),
    Vehicle \= helicopter, % A helicopter can land on a field
    sports_facility(Facility).

